Antiki -- a Xiki Clone for Sublime Text 2
=========================================

Antiki implements a tiny subset of [Xiki][] for [Sublime Text 2][ST2] and [Sublime Text 3][ST3].  It is intended to be more portable and predictable than sophisticated combination of Xiki and @lunixboch's [SublimeXiki][], while implementing the essential feature of executing shell commands and replacing them with output.

Antiki considers any line starting with `$` after zero or more tabs or spaces to be a possible command for execution.  Placing your cursor on a command and pressing either "Command+Enter" or "Control+Enter" will cause Antiki to pass the command to your shell prompt, execute it, and replace a number of subquent lines with the output.  Antiki will replace any lines with more indent than the command's indent, which effectively allows you to repeately run a command by returning your cursor to the original position and hitting "Command+Enter" again.

If you set your syntax to "Antiki", you can simply use the "Enter" key, without the "Command" or "Control" modifier, if your cursor is currently on a line starting with `$`.

This makes Antiki a great tool for writing documentation, examples and working through demos.

#### Example -- Git Commit from README.md:

For example, while hacking on an update to this README.md, Antiki was used to check `git status`:

      $ git status
        # On branch hack
        # Changes not staged for commit:
        #   (use "git add <file>..." to update what will be committed)
        #   (use "git checkout -- <file>..." to discard changes in working directory)
        #
        #   modified:   README.md
        #
        no changes added to commit (use "git add" and/or "git commit -a")

Once satisfied with the changes, the following command would submit the changes:

      $ git commit -a -m "added git commit example" --amend
        [hack 62db141] added git commit example
         1 file changed, 19 insertions(+), 13 deletions(-)

#### Example -- Documenting Remote Setups:

To duplicate the results, simply place your cursor on the command line and hit "Command+Enter" or "Control+Enter".  If your SSH agent is properly configured in your environment and loaded with your key, you can check a remote command:

      $ ssh mutation.ether uptime
         17:32:22 up 2 days, 22:39,  0 users,  load average: 0.01, 0.04, 0.05

## Features:

Antiki's insistence on being stupid and simple is its greatest advantage compared to similar implementations, making it portable, maintainable and understandable.

 - Can execute shell commands in any buffer, not just Xiki buffers.
 - Does not require anything beyond Sublime Text itself, works out of the box in Windows and OSX.
 - Passes all commands through shell, ensuring features like piping to [JQ][] or `grep` are easily available.

## Limitations:

Antiki does not provide [Xiki][] menus or use Xiki helpers.  It also does not support continuously updating output, and will hang until a command exits or ten seconds have passed -- for these features, the much more powerful [SublimeXiki][] is recommended.

## Contributors:

 - [@efi][] -- bug report and fix for windows output decoding

[Xiki]: http://xiki.org
[SublimeXiki]: https://github.com/lunixbochs/SublimeXiki
[ST2]: http://www.sublimetext.com
[ST3]: http://www.sublimetext.com
[JQ]: http://stedolan.github.com/jq/
[@efi]: https://github.com/efi
