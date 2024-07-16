# Res_unoki

Reserve Unoki-kyugijyo from the input date-time range list and account list.

- You can reserve Unoki-kyugijyo by combining the date and time list for reservations with the account list.
- You can also get a capture of the reservation list.

The only things you need to prepare are:

- datelist.txt(formated)
- accountlist.csv(formated)

## getting started
### pre-requirements
- python(3.9.7 or later)
- chromedriver(The latest version. It also needs to be compatible with the Chrome version of your browser.)

### Prepare
Follwing procedures are required only at once.

1. Get resources
   ```
   $ git clone git@github.com:ktt288/Res_unoki.git
   $ cd Res_unoki
### Run
1. Edit the datelist.txt and accountlist.csv files, making sure to adhere to the formatting rules.
   ```
   $ vi datelist.txt
   $ vi accountlist.csv
2. Run:(for reservation)
   ```
   python3 res.py
3. Check Run:(get capture of reservation list)
   ```
   python3 res_check.py
4. Winning Check Run:(Winning check and resevation fix)
   ```
   python3 winning_check.py
5. Final Check Run:(get capture of reservation fix list)
   ```
   python3 res_check.py
   
## addtional info
### Install/Update chromedrive
1. Install ChromeDriver. Note: the version of ChromeDriver need to be same with that of Chrome.
Ref: ChromeDriver Download Page
```
$brew install --cask chromedriver
$brew info chromedriver
```
2. Check PATH for ChromeDriver.
If not found, add 'export PATH="/usr/local/bin:$PATH"' to '~/.zshrc', then run '$source ~/.zshrc'. If not yet solved, reinstall ChromeDriver.
```
$which chromedriver
/usr/local/bin/chromedriver
```
3. You may have to change Privacy & Security settings to enable ChromeDriver.
click Allow Anyway botton

4. To get the latest ChromeDriver, e.g., when you update Chrome, run the following commands.
```
$brew update
$brew upgrade chromedriver
```
### self memo (TODO)
- Assuming that the time frame of Unoki is 06/08/10/12/14/16.
    January, November, December: 8 a.m. to 4 p.m.
    February, March, September, October: 7 a.m. to 5 p.m. -> Done
    April to August: 6 a.m. to 6 p.m. -> Done
    -> Program correction is required before making reservations for September and November.

