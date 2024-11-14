# xbox-kotor-sig
A very short pure Python script to sign KOTOR saves for the original Xbox.

This script generates the required `Screen.sig`, `SAVE_PARTY.sig`, `SAVE_VARS.sig`, `SAVE_INFO.sig`, `SAVE_HEADER.sig`, `SAVE_HEADERVAR.sig`, and `SAVE_DATA.sig` signature files for transferring KSE-edited Xbox saves or un-signed PC KOTOR saves to your Xbox.

## Usage
First, install Python.

Open a Terminal or CMD, and type the following:
```
git clone https://github.com/acordier16/xbox-kotor-sig/
cd xbox-kotor-sig
python xbox-kotor-sig.py MY_SAVE_FOLDER
```

The script will then use your specified input save folder to compute the sig files, and will ask whether you would like to save them on disk or not.

## More information on Xbox and KOTOR saves

For more information, check out my [blog post on the topic]().

