6 days ago
Folder: fms/config/CIA
Files:
contig-report.json
mappings-historic-av.json
mappings-historic-yt.json
mappings-history-ticker.json
mappings-portfolio. json
template-historic.json
template-history-ticker.json
template-portfolio.json
template-report.json
template-settings. json
whitelist-toolbox.json

Folder: fms/config
Files:
devops.py
exchanges.ison
regex.json
report.json
settings.json

Folder: fms/data/archive
Files:
IPHA-history.json
NVO-history.json
ROIV-history.json
SPAX.PVT-history.json
SSRM-history.json

Folder: fms/data
File: portfolio.json

Folder: fms/documentation/reference/api/alphaVantage
Files:
NEWS_SENTIMENT.json
OVERVIEW.json
QUOTE.json
TIME_SERIES_DAILY.json

Folder: fms/documentation/reference/api/yFinance
Files:
history.json
info.json
news.json
recommendations.json

Folder: fms/documentation
Files: wiki.json

Folder: fms/.github/workflows
File: cron-test.yml

Folder: fms/modules
Files:
operations.py
paginator.py

Folder: fms/scripts/config
Files:
breadcrumbs.py
colors.py
definitions.py
globals.py
input.py
introduction.py
ui.py
utils.py

Folder: fms/scripts/lib
Files:
dashboard.py
historic.py
merger.py
structure.py
verifier.py

Folder: fms/scripts
File: incubator.py

6 days ago
Yes correct, here is the final batch all of which belong in the root so inside ./fms

index.html
main.py
script.js
style.css

6 days ago
ah hahaha the configlob hahahaha that is when I originally had import ...globals as g and import ...colors as c but to make it the same as the other files I did a search and replace of 'g.' to 'glob.' and 'c.' to 'color.'.
Obviously I didnt think about 'config.' becoming 'confoglob.' hashha

6 days ago
okay so the color_plc and color_plcend stuff basically what I am trying to do and it has failed in a few places but onenplace it did work and therefor needs to be replicated as such is in main.py the options for the main menu so using your show_menu function, if you notice that when user presses 0 or just Enter (as 0 is the default) in the main menu then what happens is the exit_app function is called which baically re-colors the 3 options (1. SEARCH, 2. UPDATE and 3. CONFIG) to use color.mute while leaving the 0. EXIT as it is.
So this gives the look of those options being disabled (which they are since the script now asks for exit confirmation which requires a y or n) but without those options them dissapeaeing. UX wise it looked a bit jaggedy when they didsapear suddenly especially if the user chooses to not exit and go back as then it appears to become enabled again, I hope you know what I mean.
So there are a few places (not many) where the same thing could happen. For instance when viewing the info of the scripts which loads the entry in the wiki.json file, rather than what is happening now where we have

BACK
EXECUTE
INFO
then if user chooses 2 the EXECUTE and the INFO just dissappear, it is better if instead

BACK ← stays the same and active
EXECUTE ← either becomes inactive and colored with color.mute OR better that it remains active and the user is able to press 1 and Enter and go into the EXECUTE route directly from the INFO (wiki) page - although this functionality is not currenrly coded as at the moment the only option from the INFO view is to go back
INFO ← becomes inactive and use color.mute as we are already in the INFO page anyway.
Writing this now I just realised something, the exit_app technically the 0. EXIT should also be inactive and use color.mute also OR should change to 'N. BACK' or 'N. MAIN' to indicate pressing N would go back to the main menu???

6 days ago
Im not sure to be honedt, either A or B. C is in a way kind of okay because technically we did not exit yet so being active (display wise) is ok but its a weak argument hahaha. There is a middle groung easy option D by the way...

D) Change O to Y. and keep it as EXIT that way it is active both visually and functionaly as now the user does not see an active option with the number 0 which would not work, but instead sees the 0 change to a Y (subtle change) and pressing Y would actually result in an exit so it would no longer be misleading and would be consistent and very very easy to do, literally delete the 0 and enter an uppercase Y in the exit_app vsrsion of the options menu.
what are your thoughts?

6 days ago
yes sure go ahead
wait for your part 7 are you sure? because this was the reason I created the script.config.globals.py file, so that before those breadcrumbs are called (mostly from main.py) that the script would have already written the correct value into glob.stock_type etc before the crumb.c_... is calked to be displayed.
Or am I not understanding the way that works properly?

5 days ago
well to be honest if they need to bevome functions (which is totally fine btw) then there is no need to set the values in the globals and the value can be passed along into the function call instead.
def breadcrumbs(stock_type, user_input etc

5 days ago
So I changed the 'updater.py' back to 'updata.sh' in the render_wiki inside ui.py.
The entry inside the wiki is updata.sh. Its actually a relic from an old .sh file whichnis no longer in use.
Really the wiki needs updating to show not the two seperate filenames of incubator and updsta as incubator handles both functions of search and update.
But its a minornthing thatbI have not updated yet.

Question: This line in main.py
dev.debug = "--debug" in sys.argv
does this set the value of debug inside config/devops.py to True if executing python main.py --debug and to False if executing python main.py?

5 days ago
okay so why is it not being detected inside ./modules/operations.py?
That script still reads it as None

5 days ago
So then its useless having the debug set at all in devops, it will work better as a flag which gets passed along right?

5 days ago
ah wait so then better that main.py imports modules rather than running sub processes for operations.py, incubator.py and any other ones?

5 days ago
You've reached your daily free quota limit. It will reset at 12:00 AM UTC.

Hello, if you want to take a look at the project I have updated all the files so that the files you see here are exactly in sync with what I have on my device.
I have left a few refactor comments and checkpoints here and there inside some of the scripts.

34 minutes ago
Good question — let me lay out the tradeoff clearly.

Importing as functions (no subprocess):

✅ dev.debug and any other shared state "just works" — no CLI forwarding needed
✅ Faster (no process spawn overhead)
✅ Can pass rich Python objects directly (dicts, lists) instead of only strings via argv
✅ One shared Console() instance — no risk of clashing outputs between processes
❌ A crash in incubator.py can take down the whole main.py process instead of failing in isolation
❌ You lose the ability to run python scripts/incubator.py ... standalone from the terminal for testing/debugging — which your if __name__ == "__main__": blocks in verifier.py etc. suggest you actually rely on
❌ Heavier imports (yfinance, pandas in incubator/historic) get loaded into main.py's memory even when the user never touches search/update
Given you already lean on the standalone-testable pattern (each script has its own __main__ gate, verifier.py can literally be run alone with python scripts/lib/verifier.py), I'd lean toward keeping the subprocess architecture and just doing the small --debug forwarding fix. It's a few extra lines but it preserves your ability to isolate/test/crash-contain each stage independently — which matters a lot for a project like this where you're mid-refactor across sessions.

If you want, the middle ground is: keep subprocess for incubator.py/merger.py (the heavy, crash-prone ones with yfinance calls) but consider importing something lightweight like operations.py's backup function directly, since it's just file I/O with no risky external calls. But I'd only do that as a deliberate choice, not by default.

Now let me sync up with what you've changed on your end — reading through your refactor comments and checkpoints now.

2 ACTIONS

ACTION 1: SEARCHED DEVELOPER NOTES AND AUDITED FILES

1. I need to find every comment in the fms/ directory that looks like a refactor note, TODO, checkpoint, or marker left by the developer (things like # TODO, # FIXME, # REFACTOR, # NOTE, # CHECKPOINT, or similar inline comments indicating unfinished work or things to revisit). Search all .py files under fms/. For each one found, give me: the file path, line number, the exact comment text, and about 10 lines of surrounding code for context. Also let me know if fms/main.py, fms/modules/operations.py, fms/scripts/lib/verifier.py, fms/scripts/config/breadcrumbs.py, fms/scripts/config/input.py, or fms/scripts/config/ui.py differ from what you'd expect given they were just rewritten to: fix debug flag propagation via subprocess argv, fix import typos, convert breadcrumb strings to functions with params, add return statements. Show me their current full content too.
- $ rg -U --multiline-dotall --type py '#.*(TODO|FIXME|REFACTOR|NOTE|CHECKPOINT)' fms/
- opened main.py, operations.py, verifier.py, breadcrumbs.py, input.py, ui.py.
I have completed the search for developer notes and the audit of the recently rewritten files in the fms/ directory.

1. Developer Comments (TODO, FIXME, REFACTOR, NOTE, CHECKPOINT)
The following markers were found in the .py files under fms/:

fms/scripts/lib/structure.py
Line 121: REFACTOR
```
# === === === === === === === === R E F A C T O R
""" REFACTOR IN PROGRESS (Incomplete) :
PRIORITY: Medium
OBJECTIVE: Modify the structure.py code to use 
ui.show_menu() and inp.input() for the various
config flows. """
```
Context (Lines 111-131)
```
111:        console.print(f"[dim]TYPE[/]: [{color.info}]{type_choice}[/]")
112:        console.print(f"[dim]SCOPE[/]: [{color.info}]{scope_choice}[/]")
113:        console.print(f"[dim]SOURCE[/]: [{color.info}]{data_source}[/]")
114:        sourceKey_name = "" if data_source == "INTERNAL" else f"[dim]SOURCE KEY[/]: [{color.info}]{sourceKey}[/]"
115:        console.print(sourceKey_name)
116:        # INPUT
117:        return Confirm.ask("\nProceed?", default=True)
118:
119:
120:
121:    # === === === === === === === === R E F A C T O R
122:    """ REFACTOR IN PROGRESS (Incomplete) :
123:    PRIORITY: Medium
124:    OBJECTIVE: Modify the structure.py code to use 
125:    ui.show_menu() and inp.input() for the various
126:    config flows. """
127:
128:    # -<< STRUCTURE: ADD KEY FLOW
129:    # --- --- --- --- --- --- --- ---
130:    def structure_add_key_flow(location):
131:        # -------------------
```
fms/scripts/config/ui.py
Line 54: REFACTOR
```
# === === === === === === === === R E F A C T O R
""" REFACTOR IN PROGRESS (Incomplete) :
        OBJECTIVE:
        Modify the show_menu() code to use the
        alternating background logic as defined
        inside the show_menu_rows() function.
"""
```
Line 145: REFACTOR
```
# === === === === === === === === R E F A C T O R
```
Context (Lines 50-65)
```
50:        sys.stdout.flush()
51:
52:
53:
54:    # === === === === === === === === R E F A C T O R
55:    """ REFACTOR IN PROGRESS (Incomplete) :
56:            OBJECTIVE:
57:            Modify the show_menu() code to use the
58:            alternating background logic as defined
59:            inside the show_menu_rows() function.
60:    """
61:
62:    # -<< SHOW MENU
63:    def show_menu(breadcrumb, options, instruction="", rows=0, choice=True, prompt=""):
64:        print("\033[2J\033[H", end="")
65:        # Render FMS banner, menu breadcrumb and options
```

2. Audit of Rewritten Files
I verified the current state of the files against the expected fixes (debug flag propagation, import typos, breadcrumb conversion, and return statements).

fms/main.py
Status: Correct.
Fixes Found:
debug = " --debug" if dev.debug == True else "" (Line 39)
Subprocess calls use f"--newborn {debug}", etc. (Lines 131, 135, 139, 143).
Breadcrumbs use function calls: crumb.c_backup_preborn(stock_type, ticker) (Line 85).
Full Content: [Read fms/main.py]

fms/modules/operations.py
Status: Minor Issue Found.
Fixes Found:
Import typo fixed (Line 12: import scripts.config.colors as color).
Missing colon added to if __name__ == "__main__": block (Line 199).
Issue: Line 203 calls terminal_color(), but that function (Line 186) raises a ValueError if the Termux color file doesn't exist, which might crash on non-Termux systems.
Full Content: [Read fms/modules/operations.py]

fms/scripts/lib/verifier.py
Status: Correct.
Fixes Found:
Return statements present in verify_stock (Lines 59, 77, 86, 111, 161, 168).
Uses breadcrumb functions: crumb.c_main_search_type_input_verify(stock_type, glob.clean_input) (Line 64).
Full Content: [Read fms/scripts/lib/verifier.py]

fms/scripts/config/breadcrumbs.py
Status: Correct.
Fixes Found:
Dynamic breadcrumbs converted to functions with parameters (Lines 45, 49, 53, 56, 59, 62, 65, 68, 71, 75, 82).
Full Content: [Read fms/scripts/config/breadcrumbs.py]

fms/scripts/config/input.py
Status: Bug Detected.
Issue: Line 75 contains a typo: buffer.text.util.camel_case(). util is a separate module, so it should likely be util.camel_case(buffer.text). Also, .lowercase() (Line 75) is not a Python string method; it should be .lower().
Full Content: [Read fms/scripts/config/input.py]

fms/scripts/config/ui.py
Status: Correct.
Fixes Found:
show_menu now accepts parameters for breadcrumbs and instructions (Line 63).
Contains the REFACTOR blocks noted above.
Full Content: [Read fms/scripts/config/ui.py]

ACTION 2: ANALYZING FILE STATE AND CHECKPOINTS
Let me read the actual current files directly to get full accuracy, especially since there's a couple of issues flagged (input.py bug, ui.py refactor-in-progress).
Opened main.py, input.py, ui.py, operations.py, structure.py

The user has made substantial changes across multiple files with new functionality, but there are several bugs and incomplete refactors scattered throughout. I should identify the key issues to flag back to them, especially since they mentioned leaving refactor comments as checkpoints along the way.

Looking at the actual bugs: there's a critical timing issue where debug is computed at module load time before dev.debug is actually set, so it will always evaluate to an empty string regardless of the --debug flag. Additionally, in run_backup_process, the ops variable is only defined in certain branches but gets used unconditionally later, which would cause a NameError in several code paths like when origin is empty, --newborn, --reborn, or an unrecognized option. There's also a subprocess argument passing bug where f"--refresh{debug}" combines the flag and debug value into a single argv element instead of separate items, so the incubator script won't recognize --debug even if it were properly set. Additionally, main.py passes prompt values like "X" and "x" to ui.show_menu, but I need to verify whether the UI function checks these case-sensitively since it has checks for both uppercase and lowercase variants.

There's also a potential ordering issue in main_script_info where the wiki panel is printed after the menu prompt has already been shown, meaning users won't see the information before making their selection.

Looking at ui.py, the show_menu function now defaults rows=0 instead of the previous rows=10, which breaks the stable menu layout goal since no padding will be applied when rows isn't explicitly passed.

Scanning through main.py, none of the show_menu calls actually pass the rows parameter, so every call uses the broken default and the menu height varies unpredictably. The new clean_print approach tries to use ANSI cursor positioning with ops.terminal_size() to force instruction and prompt placement, which should work on most terminals including Termux. There's no circular import issue since operations.py doesn't import ui.py. But there's a bug in the color formatting logic where it checks key == '0.' when the actual key value being passed is something different. Rich's tag parser would interpret the [ in the ANSI escape sequence as the start of a markup tag, then look for the closing ] which it finds in the [/] closing tag, causing the parser to misinterpret the structure and likely throw a MarkupError since the content between those brackets doesn't form a valid Rich style tag.

I'm also noticing that show_menu_rows is marked as incomplete refactoring work and appears to be dead code—main.py only calls show_menu, not show_menu_rows. That's expected for work in progress.

Looking at the input.py changes, the input_field function signature includes a caller parameter with a default empty string, but the call site in main.py only passes stock_type, leaving caller empty and immediately triggering a guard condition. Line 90 would crash with NameError when the config+structure path tries to use placeholder_text since it was never assigned (the ternary operator on line 45 used comparison == instead of assignment =). Line 75 has multiple issues: buffer.text.util.camel_case() tries to call a nonexistent .util attribute on a string, .lowercase() isn't a valid method (should be .lower()), and the logic is dead code anyway since the earlier if caller == "search" branch already handles that case, so the else branch always tries to call the nonexistent .lowercase() method and crashes for any non-search caller. The mode variable gets constructed but never used anywhere in the code.

For f_width, the ternary safely avoids referencing the undefined field_width variable because Python's short-circuit evaluation means it only evaluates int(cw // 1.25) when the condition is true for non-search callers, never touching field_width. The prompt variable gets hardcoded to the same value regardless of caller context, which might be intentional for now. In operations.py, the terminal_color() function tries to read from ~/.termux/colors.properties, which will fail with FileNotFoundError on non-Termux systems like this testing environment.

There's a critical bug on line 157 where Console.print(...) calls the class method unbound instead of using the console instance, which would crash if safe_files is non-empty since the string argument gets treated as self. The exception comparison e == "" always evaluates to false, so the custom error message never displays. The call to util.pause() passes an enter="e" keyword argument that doesn't exist in the original signature, which would raise a TypeError unless the utils.py file was also updated with that parameter.

Before reporting these issues, I need to verify the current state of utils.py, colors.py, definitions.py, and globals.py since there are references to color attributes like color.r1 and color.p1 that don't match the naming conventions I saw earlier, and I should confirm whether the pause() function signature has actually been modified.

This is a substantial rewrite on your end — lots of good new functionality (retention policy in backups, cursor-positioned prompts, per-row bg support, config flows). But there are quite a few real bugs mixed in with the intentional REFACTOR-in-progress zones. Let me check a few more files to complete the picture before reporting.

Agent
So in your refactor with the show_menu you have the options list which define the number, label and label color. I wonder is it possible that the background color of those options rows can be set to a different color than whatever color the termux or cli color has?

6 days ago
ok wait, so if this is possible lets do this. add two bg colors that will be alternating colors for tge rows. Also if it is possible to have bg color on intPrompt lines as well? But no need to refactor everything just give ke the specific code for this so I can surgically add it as it is a good way for me to lesrn also

6 days ago
Is it possible within this project to upload files in storage so you can reference those?

6 days ago
ok well just so you know I am on the android mobile app. now I found the library / file tree area, I see there is already a lot of files and folders and also there is the uploaded assets which is what I uploaded in here. So would it be a good idea if I created a new folder inside the root, and then I created an exact copy of the directory structure as I have it on my device then upload all the latest files inside the matching directories? This way you can see the exact structure and it would be easier to keep in sync during development. What do you think?

6 days ago
ok so creating folders is no problem. but being able to upload a file into that folde I cant figure out how. The files get uploaded into the root and there sesms not to be a way to move the file into a folder.

6 days ago
ok so lets do this one folder as a test.

the files are all in the root directory.
so these files need to go inside

fms/config/CIA

here are the file names:

contig-report.json
mappings-historic-av.json
mappings-historic-yt.json
mappings-history-ticker.json
mappings-portfolio. json
template-historic.json
template-history-ticker.json
template-portfolio.json
template-report.json
template-settings. json
whitelist-toolbox.json

6 days ago
Folder: fms/config

Files:
devops.py
exchanges.ison
regex.json
report.json
settings.json

6 days ago
Folder: fms/data/archive
Files:
IPHA-history.json
NVO-history.json
ROIV-history.json
SPAX.PVT-history.json
SSRM-history.json

Folder: fms/data
File: portfolio.json

Folder: fms/documentation/reference/api/alphaVantage
Files:
NEWS_SENTIMENT.json
OVERVIEW.json
QUOTE.json
TIME_SERIES_DAILY.json

Folder: fms/documentation/reference/api/yFinance
Files:
history.json
info.json
news.json
recommendations.json

Folder: fms/documentation
Files: wiki.json

6 days ago
Folder: fms/.github/workflows
File: cron-test.yml

Folder: fms/modules
Files:
operations.py
paginator.py

Folder: fms/scripts/config
Files:
breadcrumbs.py
colors.py
definitions.py
globals.py
input.py
introduction.py
ui.py
utils.py

Folder: fms/scripts/lib
Files:
dashboard.py
historic.py
merger.py
structure.py
verifier.py

Folder: fms/scripts
File: incubator.py

6 days ago
Yes correct, here is the final batch all of which belong in the root so inside ./fms

index.html
main.py
script.js
style.css

6 days ago
well one thing u should be aware of. I actually suffer from chronic heart failure so even though most of my time is spent programming there are times where I do need to rest. It has been a log day sk far. but you should know I have made a fair amount of changes here and there to the files that you also refactored, so I think go ahead and take a look at those changes. They are not all complete and there for sure will be some mismatches between old and new references and stuff which will need fixing pkus im sure some typos and general incorrect code and logic here and there. but also do take a look at all of the files so you can get a feel of what the whole thing is abiut and what it is I am attempting to do.

6 days ago
ah hahaha the configlob hahahaha that is when I originally had import ...globals as g and import ...colors as c but to make it the same as the other files I did a search and replace of 'g.' to 'glob.' and 'c.' to 'color.'.
Obviously I didnt think about 'config.' becoming 'confoglob.' hashha

6 days ago
okay so the color_plc and color_plcend stuff basically what I am trying to do and it has failed in a few places but onenplace it did work and therefor needs to be replicated as such is in main.py the options for the main menu so using your show_menu function, if you notice that when user presses 0 or just Enter (as 0 is the default) in the main menu then what happens is the exit_app function is called which baically re-colors the 3 options (1. SEARCH, 2. UPDATE and 3. CONFIG) to use color.mute while leaving the 0. EXIT as it is.
So this gives the look of those options being disabled (which they are since the script now asks for exit confirmation which requires a y or n) but without those options them dissapeaeing. UX wise it looked a bit jaggedy when they didsapear suddenly especially if the user chooses to not exit and go back as then it appears to become enabled again, I hope you know what I mean.
So there are a few places (not many) where the same thing could happen. For instance when viewing the info of the scripts which loads the entry in the wiki.json file, rather than what is happening now where we have

BACK
EXECUTE
INFO
then if user chooses 2 the EXECUTE and the INFO just dissappear, it is better if instead

BACK ← stays the same and active
EXECUTE ← either becomes inactive and colored with color.mute OR better that it remains active and the user is able to press 1 and Enter and go into the EXECUTE route directly from the INFO (wiki) page - although this functionality is not currenrly coded as at the moment the only option from the INFO view is to go back
INFO ← becomes inactive and use color.mute as we are already in the INFO page anyway.
Writing this now I just realised something, the exit_app technically the 0. EXIT should also be inactive and use color.mute also OR should change to 'N. BACK' or 'N. MAIN' to indicate pressing N would go back to the main menu???

6 days ago
Im not sure to be honedt, either A or B. C is in a way kind of okay because technically we did not exit yet so being active (display wise) is ok but its a weak argument hahaha. There is a middle groung easy option D by the way...

D) Change O to Y. and keep it as EXIT that way it is active both visually and functionaly as now the user does not see an active option with the number 0 which would not work, but instead sees the 0 change to a Y (subtle change) and pressing Y would actually result in an exit so it would no longer be misleading and would be consistent and very very easy to do, literally delete the 0 and enter an uppercase Y in the exit_app vsrsion of the options menu.
what are your thoughts?

6 days ago
yes sure go ahead
wait for your part 7 are you sure? because this was the reason I created the script.config.globals.py file, so that before those breadcrumbs are called (mostly from main.py) that the script would have already written the correct value into glob.stock_type etc before the crumb.c_... is calked to be displayed.
Or am I not understanding the way that works properly?

6 days ago
well to be honest if they need to bevome functions (which is totally fine btw) then there is no need to set the values in the globals and the value can be passed along into the function call instead.
def breadcrumbs(stock_type, user_input etc

6 days ago
So I changed the 'updater.py' back to 'updata.sh' in the render_wiki inside ui.py.
The entry inside the wiki is updata.sh. Its actually a relic from an old .sh file whichnis no longer in use.
Really the wiki needs updating to show not the two seperate filenames of incubator and updsta as incubator handles both functions of search and update.
But its a minornthing thatbI have not updated yet.

Question: This line in main.py
dev.debug = "--debug" in sys.argv
does this set the value of debug inside config/devops.py to True if executing python main.py --debug and to False if executing python main.py?

5 days ago
okay so why is it not being detected inside ./modules/operations.py?
That script still reads it as None

5 days ago
So then its useless having the debug set at all in devops, it will work better as a flag which gets passed along right?

5 days ago
ah wait so then better that main.py imports modules rather than running sub processes for operations.py, incubator.py and any other ones?

5 days ago
You've reached your daily free quota limit. It will reset at 12:00 AM UTC.

Hello, if you want to take a look at the project I have updated all the files so that the files you see here are exactly in sync with what I have on my device.
I have left a few refactor comments and checkpoints here and there inside some of the scripts.

47 minutes ago
Good question — let me lay out the tradeoff clearly.

Importing as functions (no subprocess):

✅ dev.debug and any other shared state "just works" — no CLI forwarding needed
✅ Faster (no process spawn overhead)
✅ Can pass rich Python objects directly (dicts, lists) instead of only strings via argv
✅ One shared Console() instance — no risk of clashing outputs between processes
❌ A crash in incubator.py can take down the whole main.py process instead of failing in isolation
❌ You lose the ability to run python scripts/incubator.py ... standalone from the terminal for testing/debugging — which your if __name__ == "__main__": blocks in verifier.py etc. suggest you actually rely on
❌ Heavier imports (yfinance, pandas in incubator/historic) get loaded into main.py's memory even when the user never touches search/update
Given you already lean on the standalone-testable pattern (each script has its own __main__ gate, verifier.py can literally be run alone with python scripts/lib/verifier.py), I'd lean toward keeping the subprocess architecture and just doing the small --debug forwarding fix. It's a few extra lines but it preserves your ability to isolate/test/crash-contain each stage independently — which matters a lot for a project like this where you're mid-refactor across sessions.

If you want, the middle ground is: keep subprocess for incubator.py/merger.py (the heavy, crash-prone ones with yfinance calls) but consider importing something lightweight like operations.py's backup function directly, since it's just file I/O with no risky external calls. But I'd only do that as a deliberate choice, not by default.

Now let me sync up with what you've changed on your end — reading through your refactor comments and checkpoints now.

Let me read the actual current files directly to get full accuracy, especially since there's a couple of issues flagged (input.py bug, ui.py refactor-in-progress).

The user has made substantial changes across multiple files with new functionality, but there are several bugs and incomplete refactors scattered throughout. I should identify the key issues to flag back to them, especially since they mentioned leaving refactor comments as checkpoints along the way.

Looking at the actual bugs: there's a critical timing issue where debug is computed at module load time before dev.debug is actually set, so it will always evaluate to an empty string regardless of the --debug flag. Additionally, in run_backup_process, the ops variable is only defined in certain branches but gets used unconditionally later, which would cause a NameError in several code paths like when origin is empty, --newborn, --reborn, or an unrecognized option. There's also a subprocess argument passing bug where f"--refresh{debug}" combines the flag and debug value into a single argv element instead of separate items, so the incubator script won't recognize --debug even if it were properly set. Additionally, main.py passes prompt values like "X" and "x" to ui.show_menu, but I need to verify whether the UI function checks these case-sensitively since it has checks for both uppercase and lowercase variants.

There's also a potential ordering issue in main_script_info where the wiki panel is printed after the menu prompt has already been shown, meaning users won't see the information before making their selection.

Looking at ui.py, the show_menu function now defaults rows=0 instead of the previous rows=10, which breaks the stable menu layout goal since no padding will be applied when rows isn't explicitly passed.

Scanning through main.py, none of the show_menu calls actually pass the rows parameter, so every call uses the broken default and the menu height varies unpredictably. The new clean_print approach tries to use ANSI cursor positioning with ops.terminal_size() to force instruction and prompt placement, which should work on most terminals including Termux. There's no circular import issue since operations.py doesn't import ui.py. But there's a bug in the color formatting logic where it checks key == '0.' when the actual key value being passed is something different. Rich's tag parser would interpret the [ in the ANSI escape sequence as the start of a markup tag, then look for the closing ] which it finds in the [/] closing tag, causing the parser to misinterpret the structure and likely throw a MarkupError since the content between those brackets doesn't form a valid Rich style tag.

I'm also noticing that show_menu_rows is marked as incomplete refactoring work and appears to be dead code—main.py only calls show_menu, not show_menu_rows. That's expected for work in progress.

Looking at the input.py changes, the input_field function signature includes a caller parameter with a default empty string, but the call site in main.py only passes stock_type, leaving caller empty and immediately triggering a guard condition. Line 90 would crash with NameError when the config+structure path tries to use placeholder_text since it was never assigned (the ternary operator on line 45 used comparison == instead of assignment =). Line 75 has multiple issues: buffer.text.util.camel_case() tries to call a nonexistent .util attribute on a string, .lowercase() isn't a valid method (should be .lower()), and the logic is dead code anyway since the earlier if caller == "search" branch already handles that case, so the else branch always tries to call the nonexistent .lowercase() method and crashes for any non-search caller. The mode variable gets constructed but never used anywhere in the code.

For f_width, the ternary safely avoids referencing the undefined field_width variable because Python's short-circuit evaluation means it only evaluates int(cw // 1.25) when the condition is true for non-search callers, never touching field_width. The prompt variable gets hardcoded to the same value regardless of caller context, which might be intentional for now. In operations.py, the terminal_color() function tries to read from ~/.termux/colors.properties, which will fail with FileNotFoundError on non-Termux systems like this testing environment.

There's a critical bug on line 157 where Console.print(...) calls the class method unbound instead of using the console instance, which would crash if safe_files is non-empty since the string argument gets treated as self. The exception comparison e == "" always evaluates to false, so the custom error message never displays. The call to util.pause() passes an enter="e" keyword argument that doesn't exist in the original signature, which would raise a TypeError unless the utils.py file was also updated with that parameter.

Before reporting these issues, I need to verify the current state of utils.py, colors.py, definitions.py, and globals.py since there are references to color attributes like color.r1 and color.p1 that don't match the naming conventions I saw earlier, and I should confirm whether the pause() function signature has actually been modified.

This is a substantial rewrite on your end — lots of good new functionality (retention policy in backups, cursor-positioned prompts, per-row bg support, config flows). But there are quite a few real bugs mixed in with the intentional REFACTOR-in-progress zones. Let me check a few more files to complete the picture before reporting.

I've now got the full picture. There's good progress in your rewrite, but the sync introduced several bugs — some crash the three core pipelines outright. Here's what I found, split into what's genuinely broken vs. what's just your marked WIP (which I'll leave alone):

Crashes blocking --newborn/--reborn/--refresh right now:

run_backup_process() in main.py only defines the ops menu list for --refresh/--reset/--restructure/--reportfolio. For "", --newborn, --reborn, or anything unmatched, ops is never defined → crashes with NameError the moment you try to add or update a stock.
inp.input_field(stock_type=glob.stock_type) in main_search_type() doesn't pass caller=, which is required — input_field immediately returns None because its own guard clause fires ("no caller defined"). Ticker/company entry silently never works.
That guard clause also calls util.pause(...), but input.py never imports util — would crash with NameError on top of the above.
Inside the text-transform handler, buffer.text.util.camel_case() / .lowercase() aren't valid — .lowercase() isn't even a real string method. Crashes for any non-search input field (e.g. structure config).
The module-level debug = " --debug" if dev.debug == True else "" in main.py runs at import time — before dev.debug gets set in the if __name__ == "__main__": block at the bottom. So it's always "", meaning --debug never reaches your subprocesses regardless of flag.
Related: the subprocess calls jam the flag into one string (f"--newborn {debug}"), which lands as a single argv item, not two — so even after fixing #5 it wouldn't be detected by "--debug" in sys.argv on the receiving end.
Other real bugs (not in your marked REFACTOR zones):
7. ui.show_menu() now defaults rows=0, and no call site passes rows=, so the padding that keeps the screen stable never applies — this undoes goal #1 (stable layout) on every screen.

Leftover debug line in show_menu: console.print(trmx_rows, inpt_row, inst_row) prints raw numbers above every menu.
key == '0.' never matches your actual key value "0" (no period) — the special EXIT/BACK highlight color never applies.
Mixing raw ANSI cursor-move codes inside Rich markup tags in the CleanIntPrompt.ask(...) call is fragile and can throw a markup error.
operations.py: Console.print(...) uses the class, not your console instance — crashes if there are any protected backup files to list.
utils.py's pause(): references info.crmb, but info doesn't exist there (should be color.crmb) — crashes if a "bug" pause is ever triggered.
structure.py: util.util.save_json(...) (double reference) — still present, would crash on saving template/mapping changes.
I'm going to fix 1–13 now — they're unambiguous bugs, not part of your marked "REFACTOR IN PROGRESS" zones (I'm leaving show_menu_rows's alternating-bg merge and structure_add_key_flow's menu-conversion TODO exactly as you left them).

All 13 fixes are applied and verified in the file snippets above — no stray indentation or duplicate lines. Here's a quick summary of what changed:

Pipeline-blocking bugs fixed (these were stopping --newborn/--reborn/--refresh from working at all):

run_backup_process() now defines its menu options for every origin, not just some — no more crash on newborn/reborn
Ticker/company input now actually works — the missing caller="search" argument is now passed
The debug flag now correctly reaches subprocesses as its own argument, computed at the right time instead of frozen at import
Text input no longer crashes on non-search fields (structure/config keys now camelCase properly, others lowercase)
Stable-menu-layout goal (goal #1) restored:
show_menu() pads to rows=10 again, so screens no longer shift with option count
Removed a leftover debug print that was showing raw numbers above every menu
Fixed the "0" key color match so BACK/EXIT highlighting works again
Other crash fixes:

Backup listing no longer crashes when there are protected backup files (Console.print → console.print)
pause() no longer crashes when showing a "bug" message (info.crmb → color.crmb)
Template/mapping saves in structure.py no longer crash (util.util.save_json → util.save_json)
I deliberately left your two marked "REFACTOR IN PROGRESS" zones untouched — the show_menu/show_menu_rows alternating-background merge in ui.py, and the structure_add_key_flow menu-conversion TODO in structure.py. Those are clearly your own in-progress work, not accidents.

I deliberately left your two marked "REFACTOR IN PROGRESS" zones untouched — the show_menu/show_menu_rows alternating-background merge in ui.py, and the structure_add_key_flow menu-conversion TODO in structure.py. Those are clearly your own in-progress work, not accidents.

One thing I couldn't verify without running the app: the ANSI-cursor + Rich-markup prompt fix in ui.py (item #10) is a reasonable fix based on how Rich parses [...] tags, but you'll want to actually run it on your device once to confirm the cursor lands where you expect — terminal escape-code behavior can be finicky across emulators (Termux vs others).

Next, I can add a lightweight --dry-run style self-check to main.py that walks through --newborn, --reborn, and --refresh without touching your real portfolio data, so you can verify each pipeline end-to-end from your phone without risking your live JSON. Would you like me to do that?

Fix critical bugs preventing core processes from running
Jul 03, 2026, 2:22 PM
[Rollback here] [changes]

Time worked: 3 minutes
Work done: 31 actions
Items read: 2,970 lines
Code changed: +75 -63