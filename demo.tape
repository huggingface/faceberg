# Faceberg CLI demo
# Render with: vhs demo.tape
# Outputs demo.mp4 (and demo.gif) in the current directory.
#
# Requires: faceberg already installed and `hf auth login` already run
# for the account that owns the kszucs/mycatalog catalog used below.

Output demo.mp4
Output demo.gif

Set Shell "zsh"
Set FontSize 20
Set Width 1300
Set Height 700
Set Padding 20
Set Theme "iceberg-dark"
Set TypingSpeed 40ms

Hide
Type "export PS1='> '; clear"
Enter
Show

Type "faceberg kszucs/mycatalog init"
Enter
Wait+Screen@30s /Catalog initialized successfully/
Sleep 2s

Type "faceberg kszucs/mycatalog add openai/gsm8k --config main"
Enter
Wait+Screen@45s /Added openai\.gsm8k to catalog/
Sleep 2s

Type "faceberg kszucs/mycatalog quack"
Enter
Sleep 20s
Type "SELECT question[:40], answer[:40] FROM faceberg.openai.gsm8k LIMIT 3;"
Enter
Sleep 8s
Type ".quit"
Enter
Sleep 1s
