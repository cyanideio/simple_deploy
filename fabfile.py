from fabric.api import env, run, cd, sudo 
env.use_ssh_config = True
NODE_ADDRESS = "https://npm.taobao.org/mirrors/node/latest-v6.x/node-v6.9.1-linux-x64.tar.gz"
CNPM_STG = "--registry=https://registry.npm.taobao.org \
  --cache=$HOME/.npm/.cache/cnpm \
  --disturl=https://npm.taobao.org/dist \
  --userconfig=$HOME/.cnpmrc"

PM2PATH = "node_modules/pm2/bin/pm2"

def set_env(url):
    user = url.split('@')[0]
    host = url.split('@')[1]
    print host
    print user
    env.hosts = [host]
    env.user = user

def install_node():
    cmd = """
#adding yourself to the group to access /usr/local/bin
cd /usr/local/bin 

# downloads and unzips the content to _node
mkdir _node && cd _node && wget %s -O - | tar zxf - --strip-components=1 

# copy the node modules folder to the /lib/ folder
cp -r ./lib/node_modules/ /usr/local/lib/ 

# copy the /include/node folder to /usr/local/include folder
cp -r ./include/node /usr/local/include/

# copy node to the bin folder
cp bin/node /usr/local/bin/ 

## making the symbolic link to npm
ln -s "/usr/local/lib/node_modules/npm/bin/npm-cli.js" ../npm 

# print the version of node and npm
node -v
npm -v

echo '\n#alias for cnpm\nalias cnpm="npm --registry=https://registry.npm.taobao.org \
  --cache=$HOME/.npm/.cache/cnpm \
  --disturl=https://npm.taobao.org/dist \
  --userconfig=$HOME/.cnpmrc"' >> ~/.bashrc && source ~/.bashrc
    """ % NODE_ADDRESS
    run('rm -rf /usr/local/bin/_node')
    run('rm -rf _node')
    run('ME=$(whoami) ; sudo chown -R $ME /usr/local')
    run('echo "%s" > deploy.sh' % cmd)
    run('sh deploy.sh')
    print('cleaning up')
    run('rm deploy.sh') 

def uninstall_node():
    cmd = """
#! /bin/bash
# run it by: ./uninstall-node.sh
sudo rm -rf /usr/local/bin/npm
sudo rm -rf /usr/local/bin/node
sudo rm -rf /usr/local/lib/node_modules/
sudo rm -rf /usr/local/include/node/
sudo rm -rf /usr/local/share/man/man1/node.1
sudo rm -rf /usr/local/bin/_node/ 
"""
    run('echo "%s" > uninstall.sh' % cmd)
    run('sh uninstall.sh')
    print('cleaning up')
    run('rm uninstall.sh')

def deploy(repo_name):
    print("Preparing for Deployment")
    run('rm -rf %s' % repo_name)
    run('git clone git@github.com:BTCChina/%s.git' % repo_name)
    with cd(repo_name):
        run('pwd')
        run('git submodule init')
        run('git submodule update')
        run('git submodule foreach git pull origin master')
        run('echo "%(user)s"' % env)

def update(repo_name):
    with cd(repo_name):
        run('git submodule update')
        run('git submodule foreach git pull origin master')
        run('git pull')

def npm_install(repo_name):
    run('source ~/.bashrc')
    with cd(repo_name):
        run('rm -rf node_modules')
        run('npm install %s' % CNPM_STG)

def npm_test(repo_name):
    with cd(repo_name):
        run('npm test')

def pm2(repo_name, command):
    with cd(repo_name):
        if command == 'start':
            run('%s %s src/app.js' % (PM2PATH, command))
        if command in ['stop', 'restart', 'reload', 'gracefulReload']:
            run('%s %s all' % (PM2PATH, command))
        else:
            run('%s %s' % (PM2PATH, command))