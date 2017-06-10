package settings;

import settings.commands.Command;

/**
 * Created by jimneuendorf on 6/10/17.
 */
public class Finder {
    public static Command killall() {
        return new Command("killall", "Finder");
    }
}
