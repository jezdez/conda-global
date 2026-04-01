Source demos/_settings.tape

Output demos/run.gif
Output demos/run.mp4

Hide
Type `eval "$(pixi shell-hook -s bash -e dev)"`
Enter
Wait /\)/
Type `export PS1="$DEMO_PS1" && mkdir -p /tmp/.demo-home && echo 'PS1="$ "' > /tmp/.demo-home/.bash_profile && export HOME=/tmp/.demo-home`
Enter
Wait /\$/
Type `export CONDA_GLOBAL_HOME=/tmp/.cg-demo-run && rm -rf "$CONDA_GLOBAL_HOME" && export PATH="$CONDA_GLOBAL_HOME/bin:$PATH"`
Enter
Wait /\$/
Type "clear"
Enter
Wait /\$/
Show

Type "# Run a tool without installing it permanently"
Enter
Sleep 500ms

Type@80ms "conda global run ruff -- version"
Enter
Wait /\$/
Sleep 3s

Type "# The environment is cleaned up automatically"
Enter
Sleep 500ms

Type@80ms "conda global list"
Enter
Wait /\$/
Sleep 2s

Type "# Try another tool the same way"
Enter
Sleep 500ms

Type@80ms "conda global run black -- --version"
Enter
Wait /\$/
Sleep 3s
