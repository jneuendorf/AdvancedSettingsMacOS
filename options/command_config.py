from uuid import uuid4 as uuid
from textwrap import dedent

from .command import Command


# # Close any open System Preferences panes, to prevent them from overriding
# # settings we’re about to change
# osascript -e 'tell application "System Preferences" to quit'

def identity(x):
    return x

def stringify_boolean_input(input):
    return 'true' if input else 'false'

def parse_numeric_input(input):
    return float(input)

def create_input_parser(type):
    if type == 'text':
        return identity
    if type == 'number':
        return parse_numeric_input
    if type == 'boolean':
        return identity
    if type == 'select':
        return identity
    if type == 'none':
        return identity
    raise ValueError(f'No parser for type "{type}".')

def create_input_stringifier(type):
    if type == 'boolean':
        return stringify_boolean_input
    return lambda x: str(x)


default_attrs_by_type = {
    'text': {
        'style': 'width: calc(100% - 60px);',
    },
    'number': {
        'style': 'width: calc(100% - 60px);',
    },
}

def render_widgets(section_name, command_id, data):
    t = data['type']
    state = data.get('state', None)
    attrs = {
        **default_attrs_by_type.get(t, {}),
        **data.get('widget_attrs', {})
    }
    if 'placeholder' not in attrs:
        attrs['placeholder'] = data.get('default', '')

    text_based_types = ('text', 'number')
    buttoned_widget_types = text_based_types + ('select', 'none',)

    input_widget = ''
    attrs_str = ' '.join(
        f'{key}="{val}"'
        for key, val in attrs.items()
    )
    metadata = f'data-section-name="{section_name}" data-command-id="{command_id}"'

    if t in text_based_types:
        input_widget = f'<input class="input" type="{t}" {attrs_str} data-value-source>'
    elif t == 'boolean':
        uid = uuid()
        input_widget = (
            f'<div style="position: relative; top: 13px;">'
                f'<input id="switch_{uid}" type="checkbox" class="switch is-rounded is-outlined is-link is-large send-command" {metadata} data-value-source {"checked" if state == True else ""}>'
                f'<label for="switch_{uid}"></label>'
            '</div>'
        )
    elif t == 'select':
        choices = ''.join(f'<option value="{value}" {"selected" if state == value else ""}>{label}</option>' for value, label in data['choices'])
        input_widget = f'<div class="select" {attrs_str} data-value-source><select>{choices}</select></div>'

    result = f'{input_widget} '

    if t in buttoned_widget_types:
        result += f'<button class="button is-link send-command" type="button" {metadata}>OK</button>'
    result += '<br>'
    return result



raw_command_config = {
    'System': {
        'standbydelay': {
            'label': 'Set standby delay in hours (default is 1 hour).',
            'command': 'pmset -a standbydelay {0}',
            'type': 'number',
            'stringify_input': lambda hours: str(int(hours * 3600)),
            'sudo': True,
            'default': '1',
        },
        # TODO: Don't know how to reverse.
        'soundonboot': {
            'label': 'Disable the sound effects on boot',
            'command': 'nvram SystemAudioVolume=" "',
            # 'type': 'boolean',
            'type': 'none',
            'sudo': True,
        },
    },
    'General UI/UX': {
        '_meta': {
            'run_after': {
            # TODO: is cfprefsd necessary to kill?
                'command': 'killall SystemUIServer cfprefsd',
            },
        },

        'reduceTransparency': {
            'label': 'Disable transparency in the menu bar and elsewhere on Yosemite.',
            'command': 'defaults write com.apple.universalaccess reduceTransparency -bool {0}',
            'type': 'boolean',
        },
        'AppleHighlightColor': {
            'label': 'Set highlight color to',
            'command': 'defaults write NSGlobalDomain AppleHighlightColor -string "{0}"',
            'type': 'text',
            'widgets_width': 'is-half',
            'widget_attrs': {
                'placeholder': '0.764700 0.976500 0.568600',
            },
        },
        'NSTableViewDefaultSizeMode': {
            # TODO: what numbers are valid and mean what?
            'label': 'Set sidebar icon size to',
            'command': 'defaults write NSGlobalDomain NSTableViewDefaultSizeMode -int {0}',
            'type': 'number',
            'widget_attrs': {
                'placeholder': '2',
            },
        },
        'AppleShowScrollBars': {
            'label': 'When to show scrollbars.',
            'command': 'defaults write NSGlobalDomain AppleShowScrollBars -string "{0}"',
            'type': 'select',
            'choices': (
                ('WhenScrolling', 'When scrolling'),
                ('Automatic', 'Automatic'),
                ('Always', 'Always'),
            ),
            'widgets_width': 'is-two-fifths',
        },
        'NSUseAnimatedFocusRing': {
            'label': 'Disable the over-the-top focus ring animation.',
            'command': 'defaults write NSGlobalDomain NSUseAnimatedFocusRing -bool {0}',
            'type': 'boolean',
        },
        'NSScrollAnimationEnabled': {
            'label': 'Disable smooth scrolling. Uncomment if you’re on an older Mac that messes up the animation.',
            'command': 'defaults write NSGlobalDomain NSScrollAnimationEnabled -bool {0}',
            'type': 'boolean',
        },
        'NSWindowResizeTime': {
            'label': 'Increase window resize speed for Cocoa applications.',
            'command': 'defaults write NSGlobalDomain NSWindowResizeTime -float {0}',
            'type': 'number',
            'widget_attrs': {
                'placeholder': '0.001',
                'step': '0.001',
                'min': '0',
            },
        },
        'NSNavPanelExpandedStateForSaveMode': {
            'label': 'Expand save panel by default.',
            'command': 'defaults write NSGlobalDomain NSNavPanelExpandedStateForSaveMode -bool {0} && defaults write NSGlobalDomain NSNavPanelExpandedStateForSaveMode2 -bool {0}',
            'type': 'boolean',
        },
        'PMPrintingExpandedStateForPrint': {
            'label': 'Expand print panel by default.',
            'command': 'defaults write NSGlobalDomain PMPrintingExpandedStateForPrint -bool {0} && defaults write NSGlobalDomain PMPrintingExpandedStateForPrint2 -bool {0}',
            'type': 'boolean',
        },
        'NSDocumentSaveNewDocumentsToCloud': {
            'label': 'Save to disk (not to iCloud) by default.',
            'command': 'defaults write NSGlobalDomain NSDocumentSaveNewDocumentsToCloud -bool {0}',
            'type': 'boolean',
        },
        'PrintingPrefsQuitWhenFinished': {
            'label': 'Automatically quit printer app once the print jobs complete.',
            'command': 'defaults write com.apple.print.PrintingPrefs "Quit When Finished" -bool {0}',
            'type': 'boolean',
        },
        'LSQuarantine': {
            'label': 'Disable the “Are you sure you want to open this application?” dialog.',
            'command': 'defaults write com.apple.LaunchServices LSQuarantine -bool {0}',
            'type': 'boolean',
        },
        'lsregisterRemoveDuplicates': {
            'label': 'Remove duplicates in the “Open With” menu (also see `lscleanup` alias).',
            'command': '/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -kill -r -domain local -domain system -domain user',
            'type': 'none',
        },
        'NSTextShowsControlCharacters': {
            'label': (
                'Display ASCII control characters using caret notation in standard text views. '
                'Try e.g.<br><code>cd /tmp; unidecode "\\x{0000}" > cc.txt; open -e cc.txt</code>'
            ),
            'command': 'defaults write NSGlobalDomain NSTextShowsControlCharacters -bool {0}',
            'type': 'boolean',
        },
        'NSQuitAlwaysKeepsWindows': {
            'label': 'Disable Resume system-wide.',
            'command': 'defaults write com.apple.systempreferences NSQuitAlwaysKeepsWindows -bool {0}',
            'type': 'boolean',
        },
        'NSDisableAutomaticTermination': {
            'label': 'Disable automatic termination of inactive apps.',
            'command': 'defaults write NSGlobalDomain NSDisableAutomaticTermination -bool {0}',
            'type': 'boolean',
        },
        # TODO: how to revert
        'CrashReporterDialogTypeNone': {
            'label': 'Disable the crash reporter.',
            'command': 'defaults write com.apple.CrashReporter DialogType -string "none"',
            'type': 'none',
        },
        'helpviewerDevMode': {
            'label': 'Set Help Viewer windows to non-floating mode.',
            'command': 'defaults write com.apple.helpviewer DevMode -bool {0}',
            'type': 'boolean',
        },
        'UTF-8QuickLookBug': {
            'label': 'Fix for the ancient UTF-8 bug in QuickLook (https:#mths.be/bbo). <strong class="has-text-danger">This is known to cause problems in various Adobe apps.</strong> See <a href="https:#github.com/mathiasbynens/dotfiles/issues/237">this issue</a>.',
            'command': 'echo "0x08000100:0" > ~/.CFUserTextEncoding',
            'type': 'none',
        },
        'AdminHostInfo': {
            'label': 'Reveal IP address, hostname, OS version, etc. when clicking the clock in the login window.',
            'command': 'defaults write /Library/Preferences/com.apple.loginwindow AdminHostInfo HostName',
            'type': 'none',
            'sudo': True,
        },
        'setrestartfreeze': {
            'label': 'Restart automatically if the computer freezes.',
            'command': 'systemsetup -setrestartfreeze {0}',
            'type': 'boolean',
            'sudo': True,
            'stringify_input': lambda x: 'on' if x else 'off',
        },
        'setcomputersleep': {
            'label': 'Never go into computer sleep mode.',
            'command': 'systemsetup -setcomputersleep {0} > /dev/null',
            'type': 'boolean',
            'sudo': True,
            'stringify_input': lambda x: 'on' if x else 'off',
        },
        'DisableNotificationCenter': {
            'label': 'Disable Notification Center and remove the menu bar icon.',
            'command': 'launchctl unload -w /System/Library/LaunchAgents/com.apple.notificationcenterui.plist 2> /dev/null',
            'type': 'none',
        },
        'NSAutomaticCapitalizationEnabled': {
            'label': 'Disable automatic capitalization as it’s annoying when typing code.',
            'command': 'defaults write NSGlobalDomain NSAutomaticCapitalizationEnabled -bool {0}',
            'type': 'boolean',
        },
        'NSAutomaticDashSubstitutionEnabled': {
            'label': 'Disable smart dashes as they’re annoying when typing code.',
            'command': 'defaults write NSGlobalDomain NSAutomaticDashSubstitutionEnabled -bool {0}',
            'type': 'boolean',
        },
        'NSAutomaticPeriodSubstitutionEnabled': {
            'label': 'Disable automatic period substitution as it’s annoying when typing code.',
            'command': 'defaults write NSGlobalDomain NSAutomaticPeriodSubstitutionEnabled -bool {0}',
            'type': 'boolean',
        },
        'NSAutomaticQuoteSubstitutionEnabled': {
            'label': 'Disable smart quotes as they’re annoying when typing code.',
            'command': 'defaults write NSGlobalDomain NSAutomaticQuoteSubstitutionEnabled -bool {0}',
            'type': 'boolean',
        },
        'NSAutomaticSpellingCorrectionEnabled': {
            'label': 'Disable auto-correct.',
            'command': 'defaults write NSGlobalDomain NSAutomaticSpellingCorrectionEnabled -bool {0}',
            'type': 'boolean',
        },
    },
    'SSD-specific tweaks': {
        'hibernatemode': {
            'label': 'Disable hibernation (speeds up entering sleep mode).',
            'command': 'sudo pmset -a hibernatemode 0',
            'type': 'none',
            'sudo': True,
        },
        'SleepImageFile': {
            'label': 'Remove the sleep image file to save disk space.',
            'command': 'rm /private/var/vm/sleepimage && touch /private/var/vm/sleepimage && chflags uchg /private/var/vm/sleepimage',
            'type': 'none',
            'sudo': True,
        },
    },
    'Trackpad, mouse, keyboard, Bluetooth accessories, and input': {
        # # Set language and text formats
        # # Note: if you’re in the US, replace `EUR` with `USD`, `Centimeters` with
        # # `Inches`, `en_GB` with `en_US`, and `true` with `false`.
        # defaults write NSGlobalDomain AppleLanguages -array "en" "nl"
        # defaults write NSGlobalDomain AppleLocale -string "en_GB@currency=EUR"
        # defaults write NSGlobalDomain AppleMeasurementUnits -string "Centimeters"
        # defaults write NSGlobalDomain AppleMetricUnits -bool true
        'tapClick': {
            'label': 'Trackpad: enable tap to click for this user and for the login screen.',
            'command': 'defaults write com.apple.driver.AppleBluetoothMultitouch.trackpad Clicking -bool true && defaults -currentHost write NSGlobalDomain com.apple.mouse.tapBehavior -int 1 && defaults write NSGlobalDomain com.apple.mouse.tapBehavior -int 1',
            'type': 'none',
        },
        'bottomRightCornerToRightClick': {
            'label': 'Trackpad: map bottom right corner to right-click.',
            'command': (
                'defaults write com.apple.driver.AppleBluetoothMultitouch.trackpad TrackpadCornerSecondaryClick -int 2'
                ' && defaults write com.apple.driver.AppleBluetoothMultitouch.trackpad TrackpadRightClick -bool true'
                ' && defaults -currentHost write NSGlobalDomain com.apple.trackpad.trackpadCornerClickBehavior -int 1'
                ' && defaults -currentHost write NSGlobalDomain com.apple.trackpad.enableSecondaryClick -bool true'
            ),
            'type': 'none',
        },
        'naturalScrolling': {
            'label': 'Disable “natural” (Lion-style) scrolling.',
            'command': 'defaults write NSGlobalDomain com.apple.swipescrolldirection -bool {0}',
            'type': 'boolean',
        },
        'increaseSoundQualityForBluetoothHeadphones': {
            'label': 'Increase sound quality for Bluetooth headphones/headsets.',
            'command': 'defaults write com.apple.BluetoothAudioAgent "Apple Bitpool Min (editable)" -int 40',
            'type': 'none',
        },
        'AppleKeyboardUIMode': {
            'label': 'Enable full keyboard access for all controls (e.g. enable Tab in modal dialogs).',
            'command': 'defaults write NSGlobalDomain AppleKeyboardUIMode -int 3',
            'type': 'none',
        },
        'ctrlZoom': {
            'label': 'Use scroll gesture with the Ctrl (^) modifier key to zoom.',
            'command': (
                'defaults write com.apple.universalaccess closeViewScrollWheelToggle -bool true'
                ' && defaults write com.apple.universalaccess HIDScrollZoomModifierMask -int 262144'
            ),
            'type': 'none',
        },
        'closeViewZoomFollowsFocus': {
            'label': 'Follow the keyboard focus while zoomed in.',
            'command': 'defaults write com.apple.universalaccess closeViewZoomFollowsFocus -bool {0}',
            'type': 'boolean',
        },
        'ApplePressAndHoldEnabled': {
            'label': 'Disable press-and-hold for keys in favor of key repeat.',
            'command': 'defaults write NSGlobalDomain ApplePressAndHoldEnabled -bool {0}',
            'type': 'boolean',
        },
        'KeyRepeat': {
            'label': 'Set a blazingly fast keyboard repeat rate.',
            'command': 'defaults write NSGlobalDomain KeyRepeat -int 1 && defaults write NSGlobalDomain InitialKeyRepeat -int 10',
            'type': 'none',
        },
        'showInputMenu': {
            'label': 'Show language menu in the top right corner of the boot screen.',
            'command': 'defaults write /Library/Preferences/com.apple.loginwindow showInputMenu -bool {0}',
            'type': 'boolean',
            'sudo': True,
        },
        'noMediaKeysForITunes': {
            'label': 'Stop iTunes from responding to the keyboard media keys.',
            'command': 'launchctl unload -w /System/Library/LaunchAgents/com.apple.rcd.plist 2> /dev/null',
            'type': 'none',
        },
    },
    'Screen': {
        'askForPassword': {
            'label': 'Require password immediately after sleep or screen saver begins.',
            'command': 'defaults write com.apple.screensaver askForPassword -int 1 && defaults write com.apple.screensaver askForPasswordDelay -int 0',
            'type': 'none',
        },
        'screencaptureLocation': {
            'label': 'Save screenshots to the desktop.',
            'command': 'defaults write com.apple.screencapture location -string "${HOME}/Desktop"',
            'type': 'text',
        },
        'screencaptureType': {
            'label': 'Save screenshots in format',
            'command': 'defaults write com.apple.screencapture type -string "png"',
            'type': 'select',
            'choices': (
                ('png', 'PNG'),
                ('jpg', 'JPG'),
                ('gif', 'GIF'),
                ('pdf', 'PDF'),
                ('tiff', 'TIFF'),
                ('bpm', 'BMP'),
            ),
        },
        'screencaptureDisableShadow': {
            'label': 'Disable shadow in screenshots.',
            'command': 'defaults write com.apple.screencapture disable-shadow -bool {0}',
            'type': 'boolean',
        },
        'AppleFontSmoothing': {
            'label': 'Enable subpixel font rendering on non-Apple LCDs. See <a href="Reference: https://github.com/kevinSuttle/macOS-Defaults/issues/17#issuecomment-266633501">this issue</a>.',
            'command': 'defaults write NSGlobalDomain AppleFontSmoothing -int 1',
            'type': 'none',
        },
        'DisplayResolutionEnabled': {
            'label': 'Enable HiDPI display modes (requires restart).',
            'command': 'defaults write /Library/Preferences/com.apple.windowserver DisplayResolutionEnabled -bool {0}',
            'type': 'boolean',
            'sudo': True,
        },
    },
    'Finder': {
        '_meta': {
            'run_after': {
                'command': 'killall Finder',
            },
        },

        'QuitMenuItem': {
            'label': 'Allow quitting via <code>⌘ + Q</code>. Doing so will also hide desktop icons (really?).',
            'command': 'defaults write com.apple.finder QuitMenuItem -bool {0}',
            'type': 'boolean',
        },
        # TODO: this is new (tell github repo!)
        'CreateDesktop': {
            'label': 'Show icons on the desktop.',
            'command': 'defaults write com.apple.finder CreateDesktop -bool {0}',
            'type': 'boolean',
        },
        'DisableAllAnimations': {
            'label': 'Disable window animations and "Get Info" animations.',
            'command': 'defaults write com.apple.finder DisableAllAnimations -bool {0}',
            'type': 'boolean',
        },
        'newFinderLocation': {
            'label': (
                'Set Desktop as the default location for new Finder windows. '
                # 'For other paths, use <code>PfLo</code> and <code>file:///full/path/here/</code>.'
            ),
            'command': 'defaults write com.apple.finder NewWindowTarget -string "PfDe" && defaults write com.apple.finder NewWindowTargetPath -string "file://${HOME}/Desktop/"',
            'type': 'none',
        },
        'AppleShowAllFiles': {
            'label': 'Show hidden files.',
            'command': 'defaults write com.apple.finder AppleShowAllFiles -bool {0}',
            'type': 'boolean',
        },
        'ShowExternalHardDrivesOnDesktop': {
            'label': 'Show icons for external hard drives.',
            'command': 'defaults write com.apple.finder ShowExternalHardDrivesOnDesktop -bool {0}',
            'type': 'boolean',
        },
        'ShowHardDrivesOnDesktop': {
            'label': 'Show icons for hard drives.',
            'command': 'defaults write com.apple.finder ShowHardDrivesOnDesktop -bool {0}',
            'type': 'boolean',
        },
        'ShowMountedServersOnDesktop': {
            'label': 'Show icons for servers.',
            'command': 'defaults write com.apple.finder ShowMountedServersOnDesktop -bool {0}',
            'type': 'boolean',
        },
        'ShowRemovableMediaOnDesktop': {
            'label': 'Show icons for removable media.',
            'command': 'defaults write com.apple.finder ShowRemovableMediaOnDesktop -bool {0}',
            'type': 'boolean',
        },
        'AppleShowAllExtensions': {
            'label': 'Show all filename extensions.',
            'command': 'defaults write NSGlobalDomain AppleShowAllExtensions -bool {0}',
            'type': 'boolean',
        },
        'ShowStatusBar': {
            'label': 'Show status bar.',
            'command': 'defaults write com.apple.finder ShowStatusBar -bool {0}',
            'type': 'boolean',
        },
        'ShowPathbar': {
            'label': 'Show path bar.',
            'command': 'defaults write com.apple.finder ShowPathbar -bool {0}',
            'type': 'boolean',
        },
        '_FXShowPosixPathInTitle': {
            'label': 'Display full POSIX path as Finder window title.',
            'command': 'defaults write com.apple.finder _FXShowPosixPathInTitle -bool {0}',
            'type': 'boolean',
        },
        '_FXSortFoldersFirst': {
            'label': 'Keep folders on top when sorting by name.',
            'command': 'defaults write com.apple.finder _FXSortFoldersFirst -bool {0}',
            'type': 'boolean',
        },
        'FXDefaultSearchScope': {
            'label': 'When performing a search, search the current folder by default.',
            'command': 'defaults write com.apple.finder FXDefaultSearchScope -string "SCcf"',
            'type': 'none',
        },
        'FXEnableExtensionChangeWarning': {
            'label': 'Disable the warning when changing a file extension.',
            'command': 'defaults write com.apple.finder FXEnableExtensionChangeWarning -bool {0}',
            'type': 'boolean',
        },
        'DirSpringingEnabled': {
            'label': 'Enable spring loading for directories.',
            'command': 'defaults write NSGlobalDomain com.apple.springing.enabled -bool {0}',
            'type': 'boolean',
        },
        'DirSpringingDelay': {
            'label': 'Remove the spring loading delay for directories.',
            'command': 'defaults write NSGlobalDomain com.apple.springing.delay -float 0',
            'type': 'none',
        },
        'DSDontWriteStores': {
            'label': 'Avoid creating .DS_Store files on network or USB volumes.',
            'command': 'defaults write com.apple.desktopservices DSDontWriteNetworkStores -bool {0} && defaults write com.apple.desktopservices DSDontWriteUSBStores -bool {0}',
            'type': 'boolean',
        },
        'diskImageVerification': {
            'label': 'Disable disk image verification.',
            'command': 'defaults write com.apple.frameworks.diskimages skip-verify -bool {0} && defaults write com.apple.frameworks.diskimages skip-verify-locked -bool {0} && defaults write com.apple.frameworks.diskimages skip-verify-remote -bool {0}',
            'type': 'boolean',
        },
        'newFinderWindowOnVolumeMount': {
            'label': 'Automatically open a new Finder window when a volume is mounted.',
            'command': 'defaults write com.apple.frameworks.diskimages auto-open-ro-root -bool {0} && defaults write com.apple.frameworks.diskimages auto-open-rw-root -bool {0} && defaults write com.apple.finder OpenWindowForNewRemovableDisk -bool {0}',
            'type': 'boolean',
        },
        'showItemInfo': {
            'label': 'Show item info near icons on the desktop and in other icon views.',
            'command': (
                '/usr/libexec/PlistBuddy -c "Set :DesktopViewSettings:IconViewSettings:showItemInfo {0}" ~/Library/Preferences/com.apple.finder.plist'
                ' && /usr/libexec/PlistBuddy -c "Set :FK_StandardViewSettings:IconViewSettings:showItemInfo {0}" ~/Library/Preferences/com.apple.finder.plist'
                ' && /usr/libexec/PlistBuddy -c "Set :StandardViewSettings:IconViewSettings:showItemInfo {0}" ~/Library/Preferences/com.apple.finder.plist'
            ),
            'type': 'boolean',
        },
        'labelOnBottom': {
            'label': 'Show item info to the right of the icons on the desktop.',
            'command': '/usr/libexec/PlistBuddy -c "Set DesktopViewSettings:IconViewSettings:labelOnBottom {0}" ~/Library/Preferences/com.apple.finder.plist',
            'type': 'boolean',
        },
        # # Expand the following File Info panes:
        # # “General”, “Open with”, and “Sharing & Permissions”
        # defaults write com.apple.finder FXInfoPanesExpanded -dict \
        # 	General -bool true \
        # 	OpenWith -bool true \
        # 	Privileges -bool true
        'snapToGrid': {
            'label': 'Enable snap-to-grid for icons on the desktop and in other icon views.',
            'command': (
                '/usr/libexec/PlistBuddy -c "Set :DesktopViewSettings:IconViewSettings:arrangeBy grid" ~/Library/Preferences/com.apple.finder.plist'
                ' && /usr/libexec/PlistBuddy -c "Set :FK_StandardViewSettings:IconViewSettings:arrangeBy grid" ~/Library/Preferences/com.apple.finder.plist'
                ' && /usr/libexec/PlistBuddy -c "Set :StandardViewSettings:IconViewSettings:arrangeBy grid" ~/Library/Preferences/com.apple.finder.plist'
            ),
            'type': 'none',
        },
        'gridSpacing': {
            'label': 'Set grid spacing for icons on the desktop and in other icon views.',
            'command': (
                '/usr/libexec/PlistBuddy -c "Set :DesktopViewSettings:IconViewSettings:gridSpacing {0}" ~/Library/Preferences/com.apple.finder.plist'
                ' && /usr/libexec/PlistBuddy -c "Set :FK_StandardViewSettings:IconViewSettings:gridSpacing {0}" ~/Library/Preferences/com.apple.finder.plist'
                ' && /usr/libexec/PlistBuddy -c "Set :StandardViewSettings:IconViewSettings:gridSpacing {0}" ~/Library/Preferences/com.apple.finder.plist'
            ),
            'type': 'number',
            'default': 54,
        },
        'iconSize': {
            'label': 'Set the size of icons on the desktop and in other icon views.',
            'command': (
                '/usr/libexec/PlistBuddy -c "Set :DesktopViewSettings:IconViewSettings:iconSize {0}" ~/Library/Preferences/com.apple.finder.plist'
                ' && /usr/libexec/PlistBuddy -c "Set :FK_StandardViewSettings:IconViewSettings:iconSize {0}" ~/Library/Preferences/com.apple.finder.plist'
                ' && /usr/libexec/PlistBuddy -c "Set :StandardViewSettings:IconViewSettings:iconSize {0}" ~/Library/Preferences/com.apple.finder.plist'
            ),
            'type': 'number',
            'default': 64,
        },
        'FXPreferredViewStyle': {
            'label': 'Default view in all Finder windows.',
            'command': 'defaults write com.apple.finder FXPreferredViewStyle -string "{0}"',
            'type': 'select',
            'choices': (
                ('Nlsv', 'List View'),
                ('icnv', 'Icon View'),
                ('clmv', 'Column View'),
                ('Flwv', 'Cover Flow view'),
            ),
            'widgets_width': 'is-two-fifths',
        },
        'WarnOnEmptyTrash': {
            'label': 'Disable the warning before emptying the Trash.',
            'command': 'defaults write com.apple.finder WarnOnEmptyTrash -bool {0}',
            'type': 'boolean',
        },
        'BrowseAllInterfaces': {
            'label': 'Enable AirDrop over Ethernet and on unsupported Macs running Lion.',
            'command': 'defaults write com.apple.NetworkBrowser BrowseAllInterfaces -bool {0}',
            'type': 'boolean',
        },
        'showLibraryFolder': {
            'label': 'Show the <code>~/Library</code> folder.',
            'command': 'chflags nohidden ~/Library',
            'type': 'none',
        },
        'showVolumesFolder': {
            'label': 'Show the <code>/Volumes</code> folder.',
            'command': 'chflags nohidden /Volumes',
            'type': 'none',
            'sudo': True,
        },
        'removeDropboxCheckmarks': {
            'label': 'Remove Dropbox’s green checkmark icons in Finder.',
            'command': (
                'file=/Applications/Dropbox.app/Contents/Resources/emblem-dropbox-uptodate.icns; '
                '[ -e "${file}" ] && mv -f "${file}" "${file}.bak"'
            ),
            'type': 'none',
        },
        'expandInfoPanes': {
            'label': 'Expand the following File Info panes: “General”, “Open with”, and “Sharing & Permissions”.',
            'command': 'defaults write com.apple.finder FXInfoPanesExpanded -dict General -bool true OpenWith -bool true Privileges -bool true',
            'type': 'none',
        },
    },
    'Dock, Dashboard, and hot corners': {
        '_meta': {
            'run_after': {
                'command': 'killall Dock',
            },
        },

        'mouse-over-hilite-stack': {
            'label': 'Enable highlight hover effect for the grid view of a stack (Dock).',
            'command': 'defaults write com.apple.dock mouse-over-hilite-stack -bool {0}',
            'type': 'boolean',
        },
        'tilesize': {
            'label': 'Set the icon size of Dock items.',
            'command': 'defaults write com.apple.dock tilesize -int {}',
            'type': 'number',
        },
        # TODO: what choices exist?
        'mineffect': {
            'label': 'Change minimize/maximize window effect.',
            'command': 'defaults write com.apple.dock mineffect -string "{0}"',
            'type': 'select',
            'choices': (
                ('scale', 'Scale'),
            ),
            'widgets_width': 'is-one-third',
        },
        'minimize-to-application': {
            'label': 'Minimize windows into their application&rsquo;s icon.',
            'command': 'defaults write com.apple.dock minimize-to-application -bool {}',
            'type': 'boolean',
        },
        'enable-spring-load-actions-on-all-items': {
            'label': 'Enable spring loading for all Dock items.',
            'command': 'defaults write com.apple.dock enable-spring-load-actions-on-all-items -bool true',
            'type': 'boolean',
        },
        'show-process-indicators': {
            'label': 'Show indicator lights for open applications in the Dock.',
            'command': 'defaults write com.apple.dock show-process-indicators -bool {}',
            'type': 'boolean',
        },
        'persistent-apps': {
            'label': 'Wipe all (default) app icons from the Dock. This is only really useful when setting up a new Mac, or if you don’t use.',
            'command': 'defaults write com.apple.dock persistent-apps -array',
            'type': 'none',
        },
        'static-only': {
            'label': 'Show only open applications in the Dock.',
            'command': 'defaults write com.apple.dock static-only -bool {0}',
            'type': 'boolean',
        },
        'launchanim': {
            'label': 'Don’t animate opening applications from the Dock.',
            'command': 'defaults write com.apple.dock launchanim -bool {0}',
            'type': 'boolean',
        },
        # TODO: suggest reasonable numeric values
        'expose-animation-duration': {
            'label': 'Speed up Mission Control animations.',
            'command': 'defaults write com.apple.dock expose-animation-duration -float 0.1',
            'type': 'none',
        },
        'expose-group-by-app': {
            'label': 'Don’t group windows by application in Mission Control (i.e. use the old Exposé behavior instead).',
            'command': 'defaults write com.apple.dock expose-group-by-app -bool {0}',
            'type': 'boolean',
        },
        'mcx-disabled': {
            'label': 'Disable Dashboard.',
            'command': 'defaults write com.apple.dashboard mcx-disabled -bool {0}',
            'type': 'boolean',
        },
        'dashboard-in-overlay': {
            'label': 'Don’t show Dashboard as a Space.',
            'command': 'defaults write com.apple.dock dashboard-in-overlay -bool {0}',
            'type': 'boolean',
        },
        'mru-spaces': {
            'label': 'Don’t automatically rearrange Spaces based on most recent use.',
            'command': 'defaults write com.apple.dock mru-spaces -bool {0}',
            'type': 'boolean',
        },
        'autohide-delay': {
            'label': 'Set the auto-hiding Dock delay.',
            'command': 'defaults write com.apple.dock autohide-delay -float {0}',
            'type': 'number',
        },
        'autohide-time-modifier': {
            'label': 'Set the animation speed when hiding/showing the Dock.',
            'command': 'defaults write com.apple.dock autohide-time-modifier -float {0}',
            'type': 'number',
        },
        'autohide': {
            'label': 'Automatically hide and show the Dock.',
            'command': 'defaults write com.apple.dock autohide -bool {0}',
            'type': 'boolean',
        },
        'showhidden': {
            'label': 'Make Dock icons of hidden applications translucent.',
            'command': 'defaults write com.apple.dock showhidden -bool {0}',
            'type': 'boolean',
        },
        'showLaunchpadGestureEnabled': {
            'label': 'Disable the Launchpad gesture (pinch with thumb and three fingers).',
            'command': 'defaults write com.apple.dock showLaunchpadGestureEnabled -int 0',
            'type': 'none',
        },
        'ResetLaunchpad': {
            'label': 'Reset Launchpad, but keep the desktop wallpaper intact.',
            'command': 'find "${HOME}/Library/Application Support/Dock" -name "*-*.db" -maxdepth 1 -delete',
            'type': 'none',
        },
        # TODO: sudo before BOTH commands?!
        'addIOsWatchSimulatorToLaunchpad': {
            'label': 'Add iOS & Watch Simulator to Launchpad.',
            'command': 'ln -sf "/Applications/Xcode.app/Contents/Developer/Applications/Simulator.app" "/Applications/Simulator.app" && ln -sf "/Applications/Xcode.app/Contents/Developer/Applications/Simulator (Watch).app" "/Applications/Simulator (Watch).app"',
            'type': 'none',
            'sudo': True,
        },
        'spacerLeft': {
            'label': 'Add a spacer to the left side of the Dock (where the applications are).',
            'command': 'defaults write com.apple.dock persistent-apps -array-add \'{tile-data={}; tile-type="spacer-tile";}\'',
            'type': 'none',
        },
        'spacerRight': {
            'label': 'Add a spacer to the right side of the Dock (where the Trash is).',
            'command': 'defaults write com.apple.dock persistent-others -array-add \'{tile-data={}; tile-type="spacer-tile";}\'',
            'type': 'none',
        },
        # # Hot corners
        # # Possible values:
        # #  0: no-op
        # #  2: Mission Control
        # #  3: Show application windows
        # #  4: Desktop
        # #  5: Start screen saver
        # #  6: Disable screen saver
        # #  7: Dashboard
        # # 10: Put display to sleep
        # # 11: Launchpad
        # # 12: Notification Center
        # # Top left screen corner → Mission Control
        # defaults write com.apple.dock wvous-tl-corner -int 2
        # defaults write com.apple.dock wvous-tl-modifier -int 0
        # # Top right screen corner → Desktop
        # defaults write com.apple.dock wvous-tr-corner -int 4
        # defaults write com.apple.dock wvous-tr-modifier -int 0
        # # Bottom left screen corner → Start screen saver
        # defaults write com.apple.dock wvous-bl-corner -int 5
        # defaults write com.apple.dock wvous-bl-modifier -int 0
    },
    'Safari & WebKit ': {
        '_meta': {
            'run_after': {
                'command': 'killall Safari',
            },
        },

        'sendSearchQueries': {
            'label': 'Privacy: don’t send search queries to Apple.',
            'command': 'if [[ "{0}" == "true" ]]; then defaults write com.apple.Safari UniversalSearchEnabled -bool false && defaults write com.apple.Safari SuppressSearchSuggestions -bool true; else defaults write com.apple.Safari UniversalSearchEnabled -bool true && defaults write com.apple.Safari SuppressSearchSuggestions -bool false; fi',
            'type': 'boolean',
        },
        'tabHighlight': {
            'label': 'Press Tab to highlight each item on a web page.',
            'command': 'defaults write com.apple.Safari WebKitTabToLinksPreferenceKey -bool {0} && defaults write com.apple.Safari com.apple.Safari.ContentPageGroupIdentifier.WebKit2TabsToLinks -bool {0}',
            'type': 'boolean',
        },
        'ShowFullURLInSmartSearchField': {
            'label': 'Show the full URL in the address bar (note: this still hides the scheme).',
            'command': 'defaults write com.apple.Safari ShowFullURLInSmartSearchField -bool {0}',
            'type': 'boolean',
        },
        'HomePage': {
            'label': 'Set Safari’s home page to `about:blank` for faster loading.',
            'command': 'defaults write com.apple.Safari HomePage -string "{0}"',
            'type': 'text',
            'default': 'about:blank',
            'widgets_width': 'is-two-fifths',
        },
        'AutoOpenSafeDownloads': {
            'label': 'Prevent Safari from opening ‘safe’ files automatically after downloading.',
            'command': 'defaults write com.apple.Safari AutoOpenSafeDownloads -bool {0}',
            'type': 'boolean',
        },
        'WebKit2BackspaceKeyNavigationEnabled': {
            'label': 'Allow hitting the Backspace key to go to the previous page in history.',
            'command': 'defaults write com.apple.Safari com.apple.Safari.ContentPageGroupIdentifier.WebKit2BackspaceKeyNavigationEnabled -bool {0}',
            'type': 'boolean',
        },
        'ShowFavoritesBar': {
            'label': 'Hide Safari’s bookmarks bar by default.',
            'command': 'defaults write com.apple.Safari ShowFavoritesBar -bool {0}',
            'type': 'boolean',
        },
        'ShowSidebarInTopSites': {
            'label': 'Hide Safari’s sidebar in Top Sites.',
            'command': 'defaults write com.apple.Safari ShowSidebarInTopSites -bool {0}',
            'type': 'boolean',
        },
        'DebugSnapshotsUpdatePolicy': {
            'label': 'Disable Safari’s thumbnail cache for History and Top Sites.',
            'command': 'defaults write com.apple.Safari DebugSnapshotsUpdatePolicy -int 2',
            'type': 'none',
        },
        'IncludeInternalDebugMenu': {
            'label': 'Enable Safari’s debug menu.',
            'command': 'defaults write com.apple.Safari IncludeInternalDebugMenu -bool {0}',
            'type': 'boolean',
        },
        'FindOnPageMatchesWordStartsOnly': {
            'label': 'Make Safari’s search banners default to Contains instead of Starts With.',
            'command': 'defaults write com.apple.Safari FindOnPageMatchesWordStartsOnly -bool {0}',
            'type': 'boolean',
        },
        'ProxiesInBookmarksBar': {
            'label': 'Remove useless icons from Safari’s bookmarks bar.',
            'command': 'defaults write com.apple.Safari ProxiesInBookmarksBar "()"',
            'type': 'none',
        },
        'IncludeDevelopMenu': {
            'label': 'Enable the Develop menu and the Web Inspector in Safari.',
            'command': (
                'defaults write com.apple.Safari IncludeDevelopMenu -bool {0} && '
                'defaults write com.apple.Safari WebKitDeveloperExtrasEnabledPreferenceKey -bool {0} && '
                'defaults write com.apple.Safari com.apple.Safari.ContentPageGroupIdentifier.WebKit2DeveloperExtrasEnabled -bool {0}'
            ),
            'type': 'boolean',
        },
        'WebKitDeveloperExtras': {
            'label': 'Add a context menu item for showing the Web Inspector in web views.',
            'command': 'defaults write NSGlobalDomain WebKitDeveloperExtras -bool {0}',
            'type': 'boolean',
        },
        'WebContinuousSpellCheckingEnabled': {
            'label': 'Enable continuous spellchecking.',
            'command': 'defaults write com.apple.Safari WebContinuousSpellCheckingEnabled -bool {0}',
            'type': 'boolean',
        },
        'WebAutomaticSpellingCorrectionEnabled': {
            'label': 'Disable auto-correct.',
            'command': 'defaults write com.apple.Safari WebAutomaticSpellingCorrectionEnabled -bool {0}',
            'type': 'boolean',
        },
        'AutoFillFromAddressBook': {
            'label': 'Disable AutoFill for addresses.',
            'command': 'defaults write com.apple.Safari AutoFillFromAddressBook -bool {0}',
            'type': 'boolean',
        },
        'AutoFillPasswords': {
            'label': 'Disable AutoFill for passwords.',
            'command': 'defaults write com.apple.Safari AutoFillPasswords -bool {0}',
            'type': 'boolean',
        },
        'AutoFillCreditCardData': {
            'label': 'Disable AutoFill for credit card data.',
            'command': 'defaults write com.apple.Safari AutoFillCreditCardData -bool {0}',
            'type': 'boolean',
        },
        'AutoFillMiscellaneousForms': {
            'label': 'Disable AutoFill for miscellaneous data.',
            'command': 'defaults write com.apple.Safari AutoFillMiscellaneousForms -bool {0}',
            'type': 'boolean',
        },
        'WarnAboutFraudulentWebsites': {
            'label': 'Warn about fraudulent websites.',
            'command': 'defaults write com.apple.Safari WarnAboutFraudulentWebsites -bool {0}',
            'type': 'boolean',
        },
        'WebKitPluginsEnabled': {
            'label': 'Disable plug-ins.',
            'command': 'defaults write com.apple.Safari WebKitPluginsEnabled -bool {0} && defaults write com.apple.Safari com.apple.Safari.ContentPageGroupIdentifier.WebKit2PluginsEnabled -bool {0}',
            'type': 'boolean',
        },
        'WebKitJavaEnabled': {
            'label': 'Disable Java.',
            'command': 'defaults write com.apple.Safari WebKitJavaEnabled -bool {0} && defaults write com.apple.Safari com.apple.Safari.ContentPageGroupIdentifier.WebKit2JavaEnabled -bool {0}',
            'type': 'boolean',
        },
        'blockPopUps': {
            'label': 'Block pop-up windows.',
            'command': 'defaults write com.apple.Safari WebKitJavaScriptCanOpenWindowsAutomatically -bool false && defaults write com.apple.Safari com.apple.Safari.ContentPageGroupIdentifier.WebKit2JavaScriptCanOpenWindowsAutomatically -bool false',
            'type': 'boolean',
        },
        'disableAutoPlayingVideo': {
            'label': 'Disable auto-playing video.',
            'command': (
                'defaults write com.apple.Safari WebKitMediaPlaybackAllowsInline -bool {0}'
                'defaults write com.apple.SafariTechnologyPreview WebKitMediaPlaybackAllowsInline -bool {0}'
                'defaults write com.apple.Safari com.apple.Safari.ContentPageGroupIdentifier.WebKit2AllowsInlineMediaPlayback -bool {0}'
                'defaults write com.apple.SafariTechnologyPreview com.apple.Safari.ContentPageGroupIdentifier.WebKit2AllowsInlineMediaPlayback -bool {0}'
            ),
            'type': 'boolean',
        },
        'SendDoNotTrackHTTPHeader': {
            'label': 'Enable “Do Not Track”.',
            'command': 'defaults write com.apple.Safari SendDoNotTrackHTTPHeader -bool tru{0}',
            'type': 'boolean',
        },
        'InstallExtensionUpdatesAutomatically': {
            'label': 'Update extensions automatically.',
            'command': 'defaults write com.apple.Safari InstallExtensionUpdatesAutomatically -bool tru{0}',
            'type': 'boolean',
        },
    },
    'Mail': {
        '_meta': {
            'run_after': {
                'command': 'killall Mail',
            },
        },

        'DisableReplyAnimations': {
            'label': 'Disable send and reply animations.',
            'command': 'defaults write com.apple.mail DisableReplyAnimations -bool {0} && defaults write com.apple.mail DisableSendAnimations -bool {0}',
            'type': 'boolean',
        },
        'AddressesIncludeNameOnPasteboard': {
            'label': 'Copy email addresses as <code>foo@example.com</code> instead of <code>Foo Bar &lt;foo@example.com&gt;</code>.',
            'command': 'defaults write com.apple.mail AddressesIncludeNameOnPasteboard -bool {0}',
            'type': 'boolean',
        },
        'NSUserKeyEquivalents': {
            'label': 'Add the keyboard shortcut ⌘ + Enter to send an email.',
            'command': 'defaults write com.apple.mail NSUserKeyEquivalents -dict-add "Send" "@\\U21a9"',
            'type': 'none',
        },
        'DraftsViewerAttributes': {
            'label': 'Display emails in threaded mode, sorted by date (oldest at the top)',
            'command': 'defaults write com.apple.mail DraftsViewerAttributes -dict-add "DisplayInThreadedMode" -string "yes" && defaults write com.apple.mail DraftsViewerAttributes -dict-add "SortedDescending" -string "yes" && defaults write com.apple.mail DraftsViewerAttributes -dict-add "SortOrder" -string "received-date"',
            'type': 'none',
        },
        'DisableInlineAttachmentViewing': {
            'label': 'Disable inline attachments (just show the icons).',
            'command': 'defaults write com.apple.mail DisableInlineAttachmentViewing -bool {0}',
            'type': 'boolean',
        },
        'Disable automatic spell checking': {
            'label': 'Disable automatic spell checking.',
            'command': 'defaults write com.apple.mail SpellCheckingBehavior -string "NoSpellCheckingEnabled"',
            'type': 'none',
        },
    },
    'Terminal & iTerm 2': {
        '_meta': {
            'run_after': {
                'command': 'killall Terminal',
            },
        },

        'StringEncodings': {
            'label': 'Only use UTF-8.',
            'command': 'defaults write com.apple.terminal StringEncodings -array 4',
            'type': 'none',
        },
        'FocusFollowsMouse': {
            'label': 'Enable “focus follows mouse” for Terminal.app and all X11 apps, i.e. hover over a window and start typing in it without clicking first.',
            'command': (
                'defaults write com.apple.terminal FocusFollowsMouse -bool {0} && '
                'defaults write org.x.X11 wm_ffm -bool {0}'
            ),
            'type': 'boolean',
        },
        'SecureKeyboardEntry': {
            'label': 'Enable Secure Keyboard Entry. See: <a hef="https://security.stackexchange.com/a/47786/8918">https://security.stackexchange.com/a/47786/8918</a>.',
            'command': 'defaults write com.apple.terminal SecureKeyboardEntry -bool {0}',
            'type': 'boolean',
        },
        'ShowLineMarks': {
            'label': 'Disable the annoying line marks.',
            'command': 'defaults write com.apple.Terminal ShowLineMarks -int 0',
            'type': 'none',
        },
        'PromptOnQuit': {
            'label': 'Don’t display the annoying prompt when quitting iTerm',
            'command': 'defaults write com.googlecode.iterm2 PromptOnQuit -bool {0}',
            'type': 'boolean',
        },
    },
    'Time Machine': {
        'DoNotOfferNewDisksForBackup': {
            'label': 'Prevent Time Machine from prompting to use new hard drives as backup volume.',
            'command': 'defaults write com.apple.TimeMachine DoNotOfferNewDisksForBackup -bool {0}',
            'type': 'boolean',
        },
        'disablelocal': {
            'label': 'Disable local Time Machine backups.',
            'command': 'hash tmutil &> /dev/null && sudo tmutil disablelocal',
            'type': 'none',
        },
    },
    'Activity Monitor': {
        '_meta': {
            'run_after': {
                'command': 'killall "Activity Monitor"',
            },
        },

        'OpenMainWindow': {
            'label': 'Show the main window when launching Activity Monitor.',
            'command': 'defaults write com.apple.ActivityMonitor OpenMainWindow -bool {0}',
            'type': 'boolean',
        },
        # TODO: what choices exist?
        'IconType': {
            'label': 'Visualize CPU usage in the Activity Monitor Dock icon.',
            'command': 'defaults write com.apple.ActivityMonitor IconType -int 5',
            'type': 'none',
        },
        # TODO: what choices exist?
        'ShowCategory': {
            'label': 'Show all processes in Activity Monitor.',
            'command': 'defaults write com.apple.ActivityMonitor ShowCategory -int 0',
            'type': 'none',
        },
        'SortColumnCpuUsage': {
            'label': 'Sort Activity Monitor results by CPU usage.',
            'command': (
                'defaults write com.apple.ActivityMonitor SortColumn -string "CPUUsage" && '
                'defaults write com.apple.ActivityMonitor SortDirection -int 0'
            ),
            'type': 'none',
        },
    },
    'Address Book, Dashboard, iCal, TextEdit, and Disk Utility': {
        '_meta': {
            'run_after': {
                'command': 'killall "Address Book" Calendar Contacts iCal',
            },
        },

        'ABShowDebugMenu': {
            'label': 'Enable the debug menu in Address Book.',
            'command': 'defaults write com.apple.addressbook ABShowDebugMenu -bool {0}',
            'type': 'boolean',
        },
        'devmode': {
            'label': 'Enable Dashboard dev mode (allows keeping widgets on the desktop).',
            'command': 'defaults write com.apple.dashboard devmode -bool {0}',
            'type': 'boolean',
        },
        'IncludeDebugMenu': {
            'label': 'Enable the debug menu in iCal (pre-10.8).',
            'command': 'defaults write com.apple.iCal IncludeDebugMenu -bool {0}',
            'type': 'boolean',
        },
        'RichText': {
            'label': 'Use plain text mode for new TextEdit documents.',
            'command': 'defaults write com.apple.TextEdit RichText -int 0',
            'type': 'none',
        },
        'PlainTextEncoding': {
            'label': 'Open and save files as UTF-8 in TextEdit.',
            'command': (
                'defaults write com.apple.TextEdit PlainTextEncoding -int 4 && '
                'defaults write com.apple.TextEdit PlainTextEncodingForWrite -int 4'
            ),
            'type': 'none',
        },
        'DUDebugMenuEnabled': {
            'label': 'Enable the debug menu in Disk Utility.',
            'command': (
                'efaults write com.apple.DiskUtility DUDebugMenuEnabled -bool {0} && '
                'defaults write com.apple.DiskUtility advanced-image-options -bool {0}'
            ),
            'type': 'boolean',
        },
        'MGPlayMovieOnOpen': {
            'label': 'Auto-play videos when opened with QuickTime Player.',
            'command': 'defaults write com.apple.QuickTimePlayerX MGPlayMovieOnOpen -bool {0}',
            'type': 'boolean',
        },
    },
    'Mac App Store': {
        'WebKitDeveloperExtras': {
            'label': 'Enable the WebKit Developer Tools in the Mac App Store.',
            'command': 'defaults write com.apple.appstore WebKitDeveloperExtras -bool {0}',
            'type': 'boolean',
        },
        'ShowDebugMenu': {
            'label': 'Enable Debug Menu in the Mac App Store.',
            'command': 'defaults write com.apple.appstore ShowDebugMenu -bool {0}',
            'type': 'boolean',
        },
        'AutomaticCheckEnabled': {
            'label': 'Enable the automatic update check.',
            'command': 'defaults write com.apple.SoftwareUpdate AutomaticCheckEnabled -bool {0}',
            'type': 'boolean',
        },
        'ScheduleFrequency': {
            'label': 'Check for software updates daily, not just once per week.',
            'command': 'defaults write com.apple.SoftwareUpdate ScheduleFrequency -int 1',
            'type': 'none',
        },
        'AutomaticDownload': {
            'label': 'Download newly available updates in background.',
            'command': 'defaults write com.apple.SoftwareUpdate AutomaticDownload -int 1',
            'type': 'none',
        },
        'CriticalUpdateInstall': {
            'label': 'Install System data files & security updates.',
            'command': 'defaults write com.apple.SoftwareUpdate CriticalUpdateInstall -int 1',
            'type': 'none',
        },
        'ConfigDataInstall': {
            'label': 'Automatically download apps purchased on other Macs.',
            'command': 'defaults write com.apple.SoftwareUpdate ConfigDataInstall -int 1',
            'type': 'none',
        },
        'AutoUpdate': {
            'label': 'Turn on app auto-update.',
            'command': 'defaults write com.apple.commerce AutoUpdate -bool {0}',
            'type': 'boolean',
        },
        'AutoUpdateRestartRequired': {
            'label': 'Allow the App Store to reboot machine on macOS updates.',
            'command': 'defaults write com.apple.commerce AutoUpdateRestartRequired -bool {0}',
            'type': 'boolean',
        },
    },
    'Photos': {
        '_meta': {
            'run_after': {
                'command': 'killall Photos',
            },
        },

        'disableHotPlug': {
            'label': 'Prevent Photos from opening automatically when devices are plugged in.',
            'command': 'defaults -currentHost write com.apple.ImageCapture disableHotPlug -bool {0}',
            'type': 'boolean',
        },
    },
    'Messages': {
        '_meta': {
            'run_after': {
                'command': 'killall Messages',
            },
        },

        'automaticEmojiSubstitutionEnablediMessage': {
            'label': 'Disable automatic emoji substitution (i.e. use plain text smileys).',
            'command': 'defaults write com.apple.messageshelper.MessageController SOInputLineSettings -dict-add "automaticEmojiSubstitutionEnablediMessage" -bool {0}',
            'type': 'boolean',
        },
        'automaticQuoteSubstitutionEnabled': {
            'label': 'Disable smart quotes as it’s annoying for messages that contain code.',
            'command': 'defaults write com.apple.messageshelper.MessageController SOInputLineSettings -dict-add "automaticQuoteSubstitutionEnabled" -bool {0}',
            'type': 'boolean',
        },
        'continuousSpellCheckingEnabled': {
            'label': 'Disable continuous spell checking.',
            'command': 'defaults write com.apple.messageshelper.MessageController SOInputLineSettings -dict-add "continuousSpellCheckingEnabled" -bool {0}',
            'type': 'boolean',
        },
    },
    'Google Chrome & Google Chrome Canary': {
        '_meta': {
            'run_after': {
                'command': 'killall "Google Chrome" "Google Chrome Canary"',
            },
        },

        'AppleEnableSwipeNavigateWithScrolls': {
            'label': 'Disable the all too sensitive backswipe on trackpads.',
            'command': (
                'defaults write com.google.Chrome AppleEnableSwipeNavigateWithScrolls -bool {0} && '
                'defaults write com.google.Chrome.canary AppleEnableSwipeNavigateWithScrolls -bool {0}'
            ),
            'type': 'boolean',
        },
        'AppleEnableMouseSwipeNavigateWithScrolls': {
            'label': 'Disable the all too sensitive backswipe on Magic Mouse.',
            'command': (
                'defaults write com.google.Chrome AppleEnableMouseSwipeNavigateWithScrolls -bool {0} && '
                'defaults write com.google.Chrome.canary AppleEnableMouseSwipeNavigateWithScrolls -bool {0}'
            ),
            'type': 'boolean',
        },
        'DisablePrintPreview': {
            'label': 'Use the system-native print preview dialog.',
            'command': (
                'defaults write com.google.Chrome DisablePrintPreview -bool {0} && '
                'defaults write com.google.Chrome.canary DisablePrintPreview -bool {0}'
            ),
            'type': 'boolean',
        },
        'PMPrintingExpandedStateForPrint2': {
            'label': 'Expand the print dialog by default.',
            'command': (
                'defaults write com.google.Chrome PMPrintingExpandedStateForPrint2 -bool true && '
                'defaults write com.google.Chrome.canary PMPrintingExpandedStateForPrint2 -bool true'
            ),
            'type': 'boolean',
        },
    },
    'GPGMail 2': {
        'SignNewEmailsByDefault': {
            'label': 'Disable signing emails by default.',
            'command': 'defaults write ~/Library/Preferences/org.gpgtools.gpgmail SignNewEmailsByDefault -bool {0}',
            'type': 'boolean',
        },
    },
    'Opera & Opera Developer': {
        '_meta': {
            'run_after': {
                'command': 'killall Opera',
            },
        },

        'PMPrintingExpandedStateForPrint2': {
            'label': 'Expand the print dialog by default.',
            'command': 'defaults write com.operasoftware.Opera PMPrintingExpandedStateForPrint2 -boolean {0} && defaults write com.operasoftware.OperaDeveloper PMPrintingExpandedStateForPrint2 -boolean {0}',
            'type': 'boolean',
        },
    },
    'Spotlight': {
        'hide': {
            'label': 'Hide Spotlight tray-icon (and subsequent helper).',
            'command': 'chmod 600 /System/Library/CoreServices/Search.bundle/Contents/MacOS/Search',
            'type': 'none',
            'sudo': True,
        },
        'Exclusions': {
            'label': (
                'Disable Spotlight indexing for any volume that gets mounted and has not yet been indexed before. '
                'Use <code>sudo mdutil -i off "/Volumes/foo"</code> to stop indexing any volume.'
            ),
            'command': 'defaults write /.Spotlight-V100/VolumeConfiguration Exclusions -array "/Volumes"',
            'type': 'none',
            'sudo': True,
        },
        'indexingMainVolume': {
            'label': 'Make sure indexing is enabled for the main volume.',
            'command': 'mdutil -i on / > /dev/null',
            'type': 'none',
            'sudo': True,
        },
        'rebuildIndex': {
            'label': 'Rebuild the index from scratch.',
            'command': 'mdutil -E / > /dev/null',
            'type': 'none',
            'sudo': True,
        },
        # '': {
        #     'label': '.',
        #     'command': '',
        #     'type': '',
        # },
    },
}

# # Change indexing order and disable some search results
# # Yosemite-specific search results (remove them if you are using macOS 10.9 or older):
# # 	MENU_DEFINITION
# # 	MENU_CONVERSION
# # 	MENU_EXPRESSION
# # 	MENU_SPOTLIGHT_SUGGESTIONS (send search queries to Apple)
# # 	MENU_WEBSEARCH             (send search queries to Apple)
# # 	MENU_OTHER
# defaults write com.apple.spotlight orderedItems -array \
# 	'{"enabled" = 1;"name" = "APPLICATIONS";}' \
# 	'{"enabled" = 1;"name" = "SYSTEM_PREFS";}' \
# 	'{"enabled" = 1;"name" = "DIRECTORIES";}' \
# 	'{"enabled" = 1;"name" = "PDF";}' \
# 	'{"enabled" = 1;"name" = "FONTS";}' \
# 	'{"enabled" = 0;"name" = "DOCUMENTS";}' \
# 	'{"enabled" = 0;"name" = "MESSAGES";}' \
# 	'{"enabled" = 0;"name" = "CONTACT";}' \
# 	'{"enabled" = 0;"name" = "EVENT_TODO";}' \
# 	'{"enabled" = 0;"name" = "IMAGES";}' \
# 	'{"enabled" = 0;"name" = "BOOKMARKS";}' \
# 	'{"enabled" = 0;"name" = "MUSIC";}' \
# 	'{"enabled" = 0;"name" = "MOVIES";}' \
# 	'{"enabled" = 0;"name" = "PRESENTATIONS";}' \
# 	'{"enabled" = 0;"name" = "SPREADSHEETS";}' \
# 	'{"enabled" = 0;"name" = "SOURCE";}' \
# 	'{"enabled" = 0;"name" = "MENU_DEFINITION";}' \
# 	'{"enabled" = 0;"name" = "MENU_OTHER";}' \
# 	'{"enabled" = 0;"name" = "MENU_CONVERSION";}' \
# 	'{"enabled" = 0;"name" = "MENU_EXPRESSION";}' \
# 	'{"enabled" = 0;"name" = "MENU_WEBSEARCH";}' \
# 	'{"enabled" = 0;"name" = "MENU_SPOTLIGHT_SUGGESTIONS";}'
# # Load new settings before rebuilding the index
# killall mds > /dev/null 2>&1


def with_state(data):
    if 'state' in data:
        return data

    state = None
    type = data['type']
    if type == 'boolean':
        # defaults read com.apple.dock mouse-over-hilite-stack
        command = (
            data['command']
            .replace('defaults write ', 'defaults read ')
            .replace(' -bool {0}', '')
        )
        try:
            successful, response = Command.run_state(command, data)
            state = successful == True and response.strip() == '1'
        except ValueError as e:
            state = False
    elif type == 'select':
        command = (
            data['command']
            .replace('defaults write ', 'defaults read ')
        )
        try:
            successful, response = Command.run_state(command, data)
            if successful:
                state = response.strip()
        except ValueError as e:
            pass

    if state is not None:
        return {
            **data,
            'state': state,
        }
    else:
        return data

command_config = {
    section_name: {
        command_id: (
            {
                'widgets': render_widgets(section_name, command_id, with_state(data)),
                'parse_input': create_input_parser(data['type']),
                'stringify_input': create_input_stringifier(data['type']),
                **data,
            } if command_id != '_meta' else data
        )
        for command_id, data in commands.items()
    }
    for section_name, commands in raw_command_config.items()
}


# import pprint
# pp = pprint.PrettyPrinter(indent=2)
# pp.pprint(command_config)
