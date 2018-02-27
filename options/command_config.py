from uuid import uuid4 as uuid

# https:#apple.stackexchange.com/a/23514
# pw="$(osascript -e 'Tell application "System Events" to display dialog "Password:" default answer "" with hidden answer' -e 'text returned of result' 2>/dev/null)" && /
    # echo "$pw" | sudo -S stufftorunasroot
    # echo "$pw" | sudo -S -v


# # Close any open System Preferences panes, to prevent them from overriding
# # settings we’re about to change
# osascript -e 'tell application "System Preferences" to quit'


class InputError(Exception):
    def __init__(self, message='Could not parse input.', *args, **kwargs):
        super().__init__(message, *args, **kwargs)


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
            f'<div>'
                f'<input id="switch_{uid}" type="checkbox" class="switch is-rounded is-outlined is-link is-large send-command" {metadata} data-value-source>'
                f'<label for="switch_{uid}"></label>'
            '</div>'
        )
    elif t == 'select':
        choices = ''.join(f'<option value="{value}">{label}</option>' for value, label in data['choices'])
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
        # soundonboot: {
        #     label: 'Disable the sound effects on boot',
        #     command: 'nvram SystemAudioVolume=" "',
        #     type: 'boolean',
        #     sudo: True,
        # },
    },
    'General UI/UX': {
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
        'QuitMenuItem': {
            'label': 'Allow quitting via <code>⌘ + Q</code>. Doing so will also hide desktop icons (really?).',
            'command': 'defaults write com.apple.finder QuitMenuItem -bool {0}',
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
        # '': {
        #     'label': '',
        #     'command': '',
        #     'type': '',
        # },
    },
    'Safari & WebKit ': {
        # '': {
        #     'label': '',
        #     'command': '',
        #     'type': '',
        # },
    },
    'Mail': {
        # '': {
        #     'label': '',
        #     'command': '',
        #     'type': '',
        # },
    },
    'Terminal & iTerm 2': {
        # '': {
        #     'label': '',
        #     'command': '',
        #     'type': '',
        # },
    },
    'Time Machine': {
        # '': {
        #     'label': '',
        #     'command': '',
        #     'type': '',
        # },
    },
    'Activity Monitor': {
        # '': {
        #     'label': '',
        #     'command': '',
        #     'type': '',
        # },
    },
    'Address Book, Dashboard, iCal, TextEdit, and Disk Utility': {
        # '': {
        #     'label': '',
        #     'command': '',
        #     'type': '',
        # },
    },
    'Mac App Store': {
        # '': {
        #     'label': '',
        #     'command': '',
        #     'type': '',
        # },
    },
    'Photos': {
        # '': {
        #     'label': '',
        #     'command': '',
        #     'type': '',
        # },
    },
    'Messages': {
        # '': {
        #     'label': '',
        #     'command': '',
        #     'type': '',
        # },
    },
    'Google Chrome & Google Chrome Canary': {
        # '': {
        #     'label': '',
        #     'command': '',
        #     'type': '',
        # },
    },
    'GPGMail 2': {
        # '': {
        #     'label': '',
        #     'command': '',
        #     'type': '',
        # },
    },
    'Opera & Opera Developer': {
        # '': {
        #     'label': '',
        #     'command': '',
        #     'type': '',
        # },
    },
}

# ########################################/
# # Dock, Dashboard, and hot corners                                            #
# ########################################/
#
# # Enable highlight hover effect for the grid view of a stack (Dock)
# defaults write com.apple.dock mouse-over-hilite-stack -bool true
#
# # Set the icon size of Dock items to 36 pixels
# defaults write com.apple.dock tilesize -int 36
#
# # Change minimize/maximize window effect
# defaults write com.apple.dock mineffect -string "scale"
#
# # Minimize windows into their application’s icon
# defaults write com.apple.dock minimize-to-application -bool true
#
# # Enable spring loading for all Dock items
# defaults write com.apple.dock enable-spring-load-actions-on-all-items -bool true
#
# # Show indicator lights for open applications in the Dock
# defaults write com.apple.dock show-process-indicators -bool true
#
# # Wipe all (default) app icons from the Dock
# # This is only really useful when setting up a new Mac, or if you don’t use
# # the Dock to launch apps.
# #defaults write com.apple.dock persistent-apps -array
#
# # Show only open applications in the Dock
# #defaults write com.apple.dock static-only -bool true
#
# # Don’t animate opening applications from the Dock
# defaults write com.apple.dock launchanim -bool false
#
# # Speed up Mission Control animations
# defaults write com.apple.dock expose-animation-duration -float 0.1
#
# # Don’t group windows by application in Mission Control
# # (i.e. use the old Exposé behavior instead)
# defaults write com.apple.dock expose-group-by-app -bool false
#
# # Disable Dashboard
# defaults write com.apple.dashboard mcx-disabled -bool true
#
# # Don’t show Dashboard as a Space
# defaults write com.apple.dock dashboard-in-overlay -bool true
#
# # Don’t automatically rearrange Spaces based on most recent use
# defaults write com.apple.dock mru-spaces -bool false
#
# # Remove the auto-hiding Dock delay
# defaults write com.apple.dock autohide-delay -float 0
# # Remove the animation when hiding/showing the Dock
# defaults write com.apple.dock autohide-time-modifier -float 0
#
# # Automatically hide and show the Dock
# defaults write com.apple.dock autohide -bool true
#
# # Make Dock icons of hidden applications translucent
# defaults write com.apple.dock showhidden -bool true
#
# # Disable the Launchpad gesture (pinch with thumb and three fingers)
# #defaults write com.apple.dock showLaunchpadGestureEnabled -int 0
#
# # Reset Launchpad, but keep the desktop wallpaper intact
# find "${HOME}/Library/Application Support/Dock" -name "*-*.db" -maxdepth 1 -delete
#
# # Add iOS & Watch Simulator to Launchpad
# sudo ln -sf "/Applications/Xcode.app/Contents/Developer/Applications/Simulator.app" "/Applications/Simulator.app"
# sudo ln -sf "/Applications/Xcode.app/Contents/Developer/Applications/Simulator (Watch).app" "/Applications/Simulator (Watch).app"
#
# # Add a spacer to the left side of the Dock (where the applications are)
# #defaults write com.apple.dock persistent-apps -array-add '{tile-data={}; tile-type="spacer-tile";}'
# # Add a spacer to the right side of the Dock (where the Trash is)
# #defaults write com.apple.dock persistent-others -array-add '{tile-data={}; tile-type="spacer-tile";}'
#
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
#
# ########################################/
# # Safari & WebKit                                                             #
# ########################################/
#
# # Privacy: don’t send search queries to Apple
# defaults write com.apple.Safari UniversalSearchEnabled -bool false
# defaults write com.apple.Safari SuppressSearchSuggestions -bool true
#
# # Press Tab to highlight each item on a web page
# defaults write com.apple.Safari WebKitTabToLinksPreferenceKey -bool true
# defaults write com.apple.Safari com.apple.Safari.ContentPageGroupIdentifier.WebKit2TabsToLinks -bool true
#
# # Show the full URL in the address bar (note: this still hides the scheme)
# defaults write com.apple.Safari ShowFullURLInSmartSearchField -bool true
#
# # Set Safari’s home page to `about:blank` for faster loading
# defaults write com.apple.Safari HomePage -string "about:blank"
#
# # Prevent Safari from opening ‘safe’ files automatically after downloading
# defaults write com.apple.Safari AutoOpenSafeDownloads -bool false
#
# # Allow hitting the Backspace key to go to the previous page in history
# defaults write com.apple.Safari com.apple.Safari.ContentPageGroupIdentifier.WebKit2BackspaceKeyNavigationEnabled -bool true
#
# # Hide Safari’s bookmarks bar by default
# defaults write com.apple.Safari ShowFavoritesBar -bool false
#
# # Hide Safari’s sidebar in Top Sites
# defaults write com.apple.Safari ShowSidebarInTopSites -bool false
#
# # Disable Safari’s thumbnail cache for History and Top Sites
# defaults write com.apple.Safari DebugSnapshotsUpdatePolicy -int 2
#
# # Enable Safari’s debug menu
# defaults write com.apple.Safari IncludeInternalDebugMenu -bool true
#
# # Make Safari’s search banners default to Contains instead of Starts With
# defaults write com.apple.Safari FindOnPageMatchesWordStartsOnly -bool false
#
# # Remove useless icons from Safari’s bookmarks bar
# defaults write com.apple.Safari ProxiesInBookmarksBar "()"
#
# # Enable the Develop menu and the Web Inspector in Safari
# defaults write com.apple.Safari IncludeDevelopMenu -bool true
# defaults write com.apple.Safari WebKitDeveloperExtrasEnabledPreferenceKey -bool true
# defaults write com.apple.Safari com.apple.Safari.ContentPageGroupIdentifier.WebKit2DeveloperExtrasEnabled -bool true
#
# # Add a context menu item for showing the Web Inspector in web views
# defaults write NSGlobalDomain WebKitDeveloperExtras -bool true
#
# # Enable continuous spellchecking
# defaults write com.apple.Safari WebContinuousSpellCheckingEnabled -bool true
# # Disable auto-correct
# defaults write com.apple.Safari WebAutomaticSpellingCorrectionEnabled -bool false
#
# # Disable AutoFill
# defaults write com.apple.Safari AutoFillFromAddressBook -bool false
# defaults write com.apple.Safari AutoFillPasswords -bool false
# defaults write com.apple.Safari AutoFillCreditCardData -bool false
# defaults write com.apple.Safari AutoFillMiscellaneousForms -bool false
#
# # Warn about fraudulent websites
# defaults write com.apple.Safari WarnAboutFraudulentWebsites -bool true
#
# # Disable plug-ins
# defaults write com.apple.Safari WebKitPluginsEnabled -bool false
# defaults write com.apple.Safari com.apple.Safari.ContentPageGroupIdentifier.WebKit2PluginsEnabled -bool false
#
# # Disable Java
# defaults write com.apple.Safari WebKitJavaEnabled -bool false
# defaults write com.apple.Safari com.apple.Safari.ContentPageGroupIdentifier.WebKit2JavaEnabled -bool false
#
# # Block pop-up windows
# defaults write com.apple.Safari WebKitJavaScriptCanOpenWindowsAutomatically -bool false
# defaults write com.apple.Safari com.apple.Safari.ContentPageGroupIdentifier.WebKit2JavaScriptCanOpenWindowsAutomatically -bool false
#
# # Disable auto-playing video
# #defaults write com.apple.Safari WebKitMediaPlaybackAllowsInline -bool false
# #defaults write com.apple.SafariTechnologyPreview WebKitMediaPlaybackAllowsInline -bool false
# #defaults write com.apple.Safari com.apple.Safari.ContentPageGroupIdentifier.WebKit2AllowsInlineMediaPlayback -bool false
# #defaults write com.apple.SafariTechnologyPreview com.apple.Safari.ContentPageGroupIdentifier.WebKit2AllowsInlineMediaPlayback -bool false
#
# # Enable “Do Not Track”
# defaults write com.apple.Safari SendDoNotTrackHTTPHeader -bool true
#
# # Update extensions automatically
# defaults write com.apple.Safari InstallExtensionUpdatesAutomatically -bool true
#
# ########################################/
# # Mail                                                                        #
# ########################################/
#
# # Disable send and reply animations in Mail.app
# defaults write com.apple.mail DisableReplyAnimations -bool true
# defaults write com.apple.mail DisableSendAnimations -bool true
#
# # Copy email addresses as `foo@example.com` instead of `Foo Bar <foo@example.com>` in Mail.app
# defaults write com.apple.mail AddressesIncludeNameOnPasteboard -bool false
#
# # Add the keyboard shortcut ⌘ + Enter to send an email in Mail.app
# defaults write com.apple.mail NSUserKeyEquivalents -dict-add "Send" "@\U21a9"
#
# # Display emails in threaded mode, sorted by date (oldest at the top)
# defaults write com.apple.mail DraftsViewerAttributes -dict-add "DisplayInThreadedMode" -string "yes"
# defaults write com.apple.mail DraftsViewerAttributes -dict-add "SortedDescending" -string "yes"
# defaults write com.apple.mail DraftsViewerAttributes -dict-add "SortOrder" -string "received-date"
#
# # Disable inline attachments (just show the icons)
# defaults write com.apple.mail DisableInlineAttachmentViewing -bool true
#
# # Disable automatic spell checking
# defaults write com.apple.mail SpellCheckingBehavior -string "NoSpellCheckingEnabled"
#
# ########################################/
# # Spotlight                                                                   #
# ########################################/
#
# # Hide Spotlight tray-icon (and subsequent helper)
# #sudo chmod 600 /System/Library/CoreServices/Search.bundle/Contents/MacOS/Search
# # Disable Spotlight indexing for any volume that gets mounted and has not yet
# # been indexed before.
# # Use `sudo mdutil -i off "/Volumes/foo"` to stop indexing any volume.
# sudo defaults write /.Spotlight-V100/VolumeConfiguration Exclusions -array "/Volumes"
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
# # Make sure indexing is enabled for the main volume
# sudo mdutil -i on / > /dev/null
# # Rebuild the index from scratch
# sudo mdutil -E / > /dev/null
#
# ########################################/
# # Terminal & iTerm 2                                                          #
# ########################################/
#
# # Only use UTF-8 in Terminal.app
# defaults write com.apple.terminal StringEncodings -array 4
#
# # Use a modified version of the Solarized Dark theme by default in Terminal.app
# osascript <<EOD
#
# tell application "Terminal"
#
# 	local allOpenedWindows
# 	local initialOpenedWindows
# 	local windowID
# 	set themeName to "Solarized Dark xterm-256color"
#
# 	(* Store the IDs of all the open terminal windows. *)
# 	set initialOpenedWindows to id of every window
#
# 	(* Open the custom theme so that it gets added to the list
# 	   of available terminal themes (note: this will open two
# 	   additional terminal windows). *)
# 	do shell script "open '$HOME/init/" & themeName & ".terminal'"
#
# 	(* Wait a little bit to ensure that the custom theme is added. *)
# 	delay 1
#
# 	(* Set the custom theme as the default terminal theme. *)
# 	set default settings to settings set themeName
#
# 	(* Get the IDs of all the currently opened terminal windows. *)
# 	set allOpenedWindows to id of every window
#
# 	repeat with windowID in allOpenedWindows
#
# 		(* Close the additional windows that were opened in order
# 		   to add the custom theme to the list of terminal themes. *)
# 		if initialOpenedWindows does not contain windowID then
# 			close (every window whose id is windowID)
#
# 		(* Change the theme for the initial opened terminal windows
# 		   to remove the need to close them in order for the custom
# 		   theme to be applied. *)
# 		else
# 			set current settings of tabs of (every window whose id is windowID) to settings set themeName
# 		end if
#
# 	end repeat
#
# end tell
#
# EOD
#
# # Enable “focus follows mouse” for Terminal.app and all X11 apps
# # i.e. hover over a window and start typing in it without clicking first
# #defaults write com.apple.terminal FocusFollowsMouse -bool true
# #defaults write org.x.X11 wm_ffm -bool true
#
# # Enable Secure Keyboard Entry in Terminal.app
# # See: https:#security.stackexchange.com/a/47786/8918
# defaults write com.apple.terminal SecureKeyboardEntry -bool true
#
# # Disable the annoying line marks
# defaults write com.apple.Terminal ShowLineMarks -int 0
#
# # Install the Solarized Dark theme for iTerm
# open "${HOME}/init/Solarized Dark.itermcolors"
#
# # Don’t display the annoying prompt when quitting iTerm
# defaults write com.googlecode.iterm2 PromptOnQuit -bool false
#
# ########################################/
# # Time Machine                                                                #
# ########################################/
#
# # Prevent Time Machine from prompting to use new hard drives as backup volume
# defaults write com.apple.TimeMachine DoNotOfferNewDisksForBackup -bool true
#
# # Disable local Time Machine backups
# hash tmutil &> /dev/null && sudo tmutil disablelocal
#
# ########################################/
# # Activity Monitor                                                            #
# ########################################/
#
# # Show the main window when launching Activity Monitor
# defaults write com.apple.ActivityMonitor OpenMainWindow -bool true
#
# # Visualize CPU usage in the Activity Monitor Dock icon
# defaults write com.apple.ActivityMonitor IconType -int 5
#
# # Show all processes in Activity Monitor
# defaults write com.apple.ActivityMonitor ShowCategory -int 0
#
# # Sort Activity Monitor results by CPU usage
# defaults write com.apple.ActivityMonitor SortColumn -string "CPUUsage"
# defaults write com.apple.ActivityMonitor SortDirection -int 0
#
# ########################################/
# # Address Book, Dashboard, iCal, TextEdit, and Disk Utility                   #
# ########################################/
#
# # Enable the debug menu in Address Book
# defaults write com.apple.addressbook ABShowDebugMenu -bool true
#
# # Enable Dashboard dev mode (allows keeping widgets on the desktop)
# defaults write com.apple.dashboard devmode -bool true
#
# # Enable the debug menu in iCal (pre-10.8)
# defaults write com.apple.iCal IncludeDebugMenu -bool true
#
# # Use plain text mode for new TextEdit documents
# defaults write com.apple.TextEdit RichText -int 0
# # Open and save files as UTF-8 in TextEdit
# defaults write com.apple.TextEdit PlainTextEncoding -int 4
# defaults write com.apple.TextEdit PlainTextEncodingForWrite -int 4
#
# # Enable the debug menu in Disk Utility
# defaults write com.apple.DiskUtility DUDebugMenuEnabled -bool true
# defaults write com.apple.DiskUtility advanced-image-options -bool true
#
# # Auto-play videos when opened with QuickTime Player
# defaults write com.apple.QuickTimePlayerX MGPlayMovieOnOpen -bool true
#
# ########################################/
# # Mac App Store                                                               #
# ########################################/
#
# # Enable the WebKit Developer Tools in the Mac App Store
# defaults write com.apple.appstore WebKitDeveloperExtras -bool true
#
# # Enable Debug Menu in the Mac App Store
# defaults write com.apple.appstore ShowDebugMenu -bool true
#
# # Enable the automatic update check
# defaults write com.apple.SoftwareUpdate AutomaticCheckEnabled -bool true
#
# # Check for software updates daily, not just once per week
# defaults write com.apple.SoftwareUpdate ScheduleFrequency -int 1
#
# # Download newly available updates in background
# defaults write com.apple.SoftwareUpdate AutomaticDownload -int 1
#
# # Install System data files & security updates
# defaults write com.apple.SoftwareUpdate CriticalUpdateInstall -int 1
#
# # Automatically download apps purchased on other Macs
# defaults write com.apple.SoftwareUpdate ConfigDataInstall -int 1
#
# # Turn on app auto-update
# defaults write com.apple.commerce AutoUpdate -bool true
#
# # Allow the App Store to reboot machine on macOS updates
# defaults write com.apple.commerce AutoUpdateRestartRequired -bool true
#
# ########################################/
# # Photos                                                                      #
# ########################################/
#
# # Prevent Photos from opening automatically when devices are plugged in
# defaults -currentHost write com.apple.ImageCapture disableHotPlug -bool true
#
# ########################################/
# # Messages                                                                    #
# ########################################/
#
# # Disable automatic emoji substitution (i.e. use plain text smileys)
# defaults write com.apple.messageshelper.MessageController SOInputLineSettings -dict-add "automaticEmojiSubstitutionEnablediMessage" -bool false
#
# # Disable smart quotes as it’s annoying for messages that contain code
# defaults write com.apple.messageshelper.MessageController SOInputLineSettings -dict-add "automaticQuoteSubstitutionEnabled" -bool false
#
# # Disable continuous spell checking
# defaults write com.apple.messageshelper.MessageController SOInputLineSettings -dict-add "continuousSpellCheckingEnabled" -bool false
#
# ########################################/
# # Google Chrome & Google Chrome Canary                                        #
# ########################################/
#
# # Disable the all too sensitive backswipe on trackpads
# defaults write com.google.Chrome AppleEnableSwipeNavigateWithScrolls -bool false
# defaults write com.google.Chrome.canary AppleEnableSwipeNavigateWithScrolls -bool false
#
# # Disable the all too sensitive backswipe on Magic Mouse
# defaults write com.google.Chrome AppleEnableMouseSwipeNavigateWithScrolls -bool false
# defaults write com.google.Chrome.canary AppleEnableMouseSwipeNavigateWithScrolls -bool false
#
# # Use the system-native print preview dialog
# defaults write com.google.Chrome DisablePrintPreview -bool true
# defaults write com.google.Chrome.canary DisablePrintPreview -bool true
#
# # Expand the print dialog by default
# defaults write com.google.Chrome PMPrintingExpandedStateForPrint2 -bool true
# defaults write com.google.Chrome.canary PMPrintingExpandedStateForPrint2 -bool true
#
# ########################################/
# # GPGMail 2                                                                   #
# ########################################/
#
# # Disable signing emails by default
# defaults write ~/Library/Preferences/org.gpgtools.gpgmail SignNewEmailsByDefault -bool false
#
# ########################################/
# # Opera & Opera Developer                                                     #
# ########################################/
#
# # Expand the print dialog by default
# defaults write com.operasoftware.Opera PMPrintingExpandedStateForPrint2 -boolean true
# defaults write com.operasoftware.OperaDeveloper PMPrintingExpandedStateForPrint2 -boolean true
#
# ########################################/
# # Kill affected applications                                                  #
# ########################################/
#
# for app in "Activity Monitor" \
# 	"Address Book" \
# 	"Calendar" \
# 	"cfprefsd" \
# 	"Contacts" \
# 	"Dock" \
# 	"Finder" \
# 	"Google Chrome Canary" \
# 	"Google Chrome" \
# 	"Mail" \
# 	"Messages" \
# 	"Opera" \
# 	"Photos" \
# 	"Safari" \
# 	"SystemUIServer" \
# 	"Terminal" \
# 	"iCal"; do
# 	killall "${app}" &> /dev/null
# done
# echo "Done. Note that some of these changes require a logout/restart to take effect."
#


command_config = {
    section_name: {
        command_id: {
            'widgets': render_widgets(section_name, command_id, data),
            'parse_input': create_input_parser(data['type']),
            'stringify_input': create_input_stringifier(data['type']),
            **data
        }
        for command_id, data in commands.items()
    }
    for section_name, commands in raw_command_config.items()
}

print(command_config)
