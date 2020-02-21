import os
import time
from getpass import getpass
from urllib import urlencode
from urllib2 import Request, urlopen
from pybitbucket.auth import BasicAuthenticator
from pybitbucket.bitbucket import Client
from pybitbucket.repository import Repository, RepositoryPayload, RepositoryRole, RepositoryType, RepositoryForkPolicy

# use app password when 2 factor authentication is enabled.
# see: https://developer.atlassian.com/bitbucket/api/2/reference/meta/authentication#app-pw
username = ''
password = ''
teamname = ''
hgprefix = '(Mercurial)'

if not username:
  username = raw_input('Enter your bitbucket username: ')
  if not teamname:
    teamname = raw_input('Enter your bitbucket teamname (leave empty if you don\'t need it): ')
if not teamname: 
  teamname = username
if not password:
  password = getpass(prompt='Enter your bitbucket password: ')
if not username or not teamname or not password:
  print('Username and password must be provided.')
  exit(0)

bitbucket = Client(
    BasicAuthenticator(
        username,
        password,
        ''
    )
)

for repo in Repository.find_repositories_by_owner_and_role(owner=teamname, role=RepositoryRole.MEMBER.value, client=bitbucket):
  if repo.scm != RepositoryType.HG.value:
    continue
  if repo.name.startswith(hgprefix):
    continue

  hg_clone_https = ''
  for clone in repo.links['clone']:
    if clone['name'] == 'https':
      hg_clone_https = clone['href']
      break
  hg_clone_https = hg_clone_https.replace('@', ':%s@' % password)

  print('\n\n================================================================================================')
  print('Cloning remote hg repo: %s' % repo.name)
  hg_clone_dir = 'hg-repos/%s' % repo.slug
  os.popen('rm -rf %s' % hg_clone_dir)
  hg_clone_command = "hg clone %s %s" % (hg_clone_https, hg_clone_dir)
  os.popen(hg_clone_command)

  print('Creating local git repo...')
  git_clone_dir = 'git-repos/%s' % repo.slug
  os.popen('rm -rf %s' % git_clone_dir)
  os.popen('mkdir -p %s' % git_clone_dir)
  os.popen('git init %s' % git_clone_dir)
  
  print('Migrating local hg repo to git...')
  convert_command = 'cd %s;../../fast-export/hg-fast-export.sh -r ../../%s --force' % (git_clone_dir, hg_clone_dir)
  os.popen(convert_command)
  os.popen('cd %s; git checkout HEAD' % git_clone_dir)

  print('Renaming remote hg repo...')
  url = repo.links['self']['href']
  auth = '%s:%s' % (username, password)
  auth = {'Authorization': 'Basic %s' % (auth.encode('base64').strip())}
  request = Request(url, urlencode(dict(name='%s %s' % (hgprefix, repo.name))), auth)
  request.get_method = lambda: 'PUT'
  try:
    result = urlopen(request).read()
  except Exception as e:
    print(repr(e))
    break

  print('Creating remote git repo...')
  payload = RepositoryPayload() \
    .add_scm(RepositoryType.GIT) \
    .add_name(str(repo.name)) \
    .add_is_private(repo.is_private) \
    .add_description(str(repo.description)) \
    .add_fork_policy(RepositoryForkPolicy.ALLOW_FORKS) \
    .add_language(str(repo.language)) \
    .add_has_issues(repo.has_issues) \
    .add_has_wiki(repo.has_wiki)
  repo = Repository.create(payload, repository_name=repo.slug, owner=teamname, client=bitbucket)

  git_clone_https = ''
  for clone in repo.links['clone']:
    if clone['name'] == 'https':
      git_clone_https = clone['href']
      break
  git_clone_https = git_clone_https.replace('@', ':%s@' % password)
  time.sleep(2)

  print('Pushing to remote git repo...')
  os.popen('cd %s;git remote add origin %s' % (git_clone_dir, git_clone_https))
  os.popen('cd %s;git push origin master' % (git_clone_dir))
