Source demos/_settings.tape

Output demos/quickstart.gif
Output demos/quickstart.mp4

Hide
Type `eval "$(pixi shell-hook -s bash -e dev)"`
Enter
Wait /\)/
Type `export PS1="$DEMO_PS1" && mkdir -p /tmp/.demo-home && echo 'PS1="$ "' > /tmp/.demo-home/.bash_profile && export HOME=/tmp/.demo-home`
Enter
Wait /\$/
Type `export CONDA_GLOBAL_HOME=/tmp/.cg-demo-quickstart && rm -rf "$CONDA_GLOBAL_HOME" && export PATH="$CONDA_GLOBAL_HOME/bin:$PATH"`
Enter
Wait /\$/
Type "clear"
Enter
Wait /\$/
Show

Type "# Install ruff into its own isolated environment"
Enter
Sleep 500ms

Type@80ms "conda global install ruff"
Enter
Wait /\$/
Sleep 2s

Type "# It's immediately available — no activate needed"
Enter
Sleep 500ms

Type@80ms "ruff version"
Enter
Wait /\$/
Sleep 2s

Type "# List installed tools"
Enter
Sleep 500ms

Type@80ms "conda global list"
Enter
Wait /\$/
Sleep 3s

Type "# Show the dependency tree"
Enter
Sleep 500ms

Type@80ms "conda global tree -e ruff"
Enter
Wait /\$/
Sleep 3s

Type "# Clean up"
Enter
Sleep 500ms

Type@80ms "conda global uninstall -e ruff"
Enter
Wait /\$/
Sleep 2s
