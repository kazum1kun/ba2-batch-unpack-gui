## What is this?

After two months of development, I present you - the Unpackrr, the evolution of the [original Batch BA2 Unpacker](https://www.nexusmods.com/fallout4/mods/79593/). 
Unpackrr is a graphical application that automatically extracts extra small ba2 files to keep your LO under BA2 limit 
(typically 255 files). You can specify your own file size thresholds, manage file extensions, and manage excluded files 
(w/ regex if you prefer 😎).

With Unpackrr you can also check your BA2 files for possible corruptions. Corrupted BA2s can cause weird 
looking/pixelated textures, or crash your game. You can check all BA2s in your mod folder with one click, and you can 
see which files have failed the check.

Unpackrr is intuitive to use and put you in control. You can see all the information at a glance, and you can customize 
the extraction behavior. Unpackrr keeps you informed and make sure you are aware of any issues. It automatically saves 
a copy of the ba2 files extracted, just in case something funny happens to your game. It comes in Light/Dark theme, and 
customizable color. Multi-language support.

## How to use

Note: this program is intended to be used standalone. I do not know what happens if you install it as a mod 
in your mod manager.

**If you want to extract ba2 files...**

Most features are self-explanatory and behaves exactly how you think it works. A typical flow goes like this

1. Select (or drag-and-drop) your Fallout 4 mod folder. It should be your overall mod folder where you can see individual mods.
   In MO2 it's Open > Open Mods folder. In Vortex, it's Open > Open Mod Staging Folder.
2. You can see a preview of what is going to be extracted, along with some stats.
   Double click a file to open it for further inspection, if you have an external BA2 application installed. Right click a file to bring up more options.
3. (Optional) click "Auto" to have Unpackrr pick a suitable threshold for you to get under BA2 limit, or manually enter a threshold.
4. Hit "Start" and watch the magic happen :)

For fine controls over the extraction, please check the Settings available.

**If you want to check for corrupted ba2 files...**

1. Click the "Check Files" tab on the left. Select (or drag-and-drop) your Fallout 4 mod folder.
2. Hit "Start" and watch the... magic 2 happen :)

Optionally, for a more thorough check, enable the "Deep scan" option. Normally Unpackrr checks a ba2 file by listing its 
file content, during which a corrupted ba2 will return some error. Deep scanning extracts the ba2 file to a temporary 
location and make sure everything runs correctly. Don't worry, the extracted files are automatically deleted afterward. 
Normal scans are usually sufficient to uncover corrupted files, as deep scans can take very long to finish.

DISCLAIMER: Unpackrr is unable to detect all possible archive errors, especially if the said archive can be 
listed/extracted successfully.

## Technical stuff
Unpackrr will extract all files shown in the "Preview" screen. Specifically, a file satisfying all 
the following criteria will be extracted:

- it contains any of the entries in "Postfixes"
- it does not contain any of the entries in "Ignored files"
- it is smaller than the file size threshold (unless you did not specify one)

### Settings, explained

**Extraction**

- **Postfixes**: any files containing these postfixes will be selected. A sensible default has been provided, but you can add or delete your own postfixes if you like.
- **Ignored** files: any files containing these entries will be excluded. You can add anything to the section.
  Advanced usage: you can use any regex for filtering. Wrap your pattern in `{}` (a pair of curly braces). For example, `{.*[dD]iamond.*}` matches any file that contains "diamond" or "Diamond" in the name.
  Note: matches are checked via `re.fullmatch()` function, which means it is anchored at the start and the end (i.e. `^pattern$`).
- **Ignore bad files**: self-explanatory.
- **Automatic backup**: automatically back up extracted ba2 to "backup" folder (inside individual mods' folder). You can customize where it backs up to in Advanced > Backup path

**Personalization**

- Everything is self-explanatory

**Update**

- Please note that "Check for updates" does not function currently. Please track this mod on Nexus or Watch this project on GitHub for time being.

**Advanced**

- **Show log output**: when toggled on, you can see a separate window containing all the logs collected in this run. It is helpful to provide relevant entries in the log when you file a bug report.
- **Extraction path**: by default Unpackrr extracts the ba2 in-place (typical setup for those looking to trim down their load order). However, you can elect to extract the ba2 to a separate folder by providing the (full) path to the folder of your choosing. Alternatively you can enter a relative path (e.g. "extracted") so that all files are extracted to this folder inside individual mod folders.
- **Backup path**: by default, Unpackrr saves a copy of the ba2 files extracted to "backup" folder inside individual mod folders. You can change this to a central location by providing the (full) path to the folder of your choosing. Similar to extraction path you can also enter a relative path so ba2 will be saved to this folder inside individual mod folders.
- **External ba2 tool**: the Unpackrr will automatically detect and populate the default application that handles .ba2 format in your system, however you can also specify your own program to do this. This chosen application will then be used to open ba2 files in the Preview table.
  When you "Open" a ba2, Unpackrr calls the function with the path to ba2 as its sole argument. Therefore, it is possible that some external program fails to open. Known working program includes [BSA Browser](https://www.nexusmods.com/fallout4/mods/17061), [Archive2](https://store.steampowered.com/app/1946160/Fallout_4_Creation_Kit/).

## FAQ & Known Issues

### FAQ

- Q: Unpackrr?
  A: Yes.
- Q: Linux/macOS support?
  A: not planned yet, though I can evaluate the possibilities once there's enough demand for it.


**Known Issues**

- Unpackrr can trigger false AV positives. This is due to PyInstaller that packs the program ([#1](https://github.com/kazum1kun/ba2-batch-unpack-gui/issues/1)).
- ~~The stats above the Preview section sometimes does not update when you input a threshold ([#2](https://github.com/kazum1kun/ba2-batch-unpack-gui/issues/2)).~~ Fixed in 0.2.0
- Unpackrr can take long to start sometimes ([#3](https://github.com/kazum1kun/ba2-batch-unpack-gui/issues/3)).
- ~~The file checker does not work well.~~ Fixed in 0.2.0

As always, should you encounter additional issues please don't hesitate to report. Thanks!

**Issues? Feedback?**
Please enter an [Issue](https://github.com/kazum1kun/ba2-batch-unpack-gui/issues/)/PR on GitHub. Your contribution is greatly appreciated!