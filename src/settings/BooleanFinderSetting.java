package settings;

import settings.commands.CommandSequence;
import settings.commands.RunnableCommand;

/**
 * Created by jimneuendorf on 6/10/17.
 */
public class BooleanFinderSetting extends BooleanSetting {

    public BooleanFinderSetting(String name, RunnableCommand commandTrue, RunnableCommand commandFalse, RunnableCommand commandIsActive, boolean invertedWording) {
        super(name, commandTrue, commandFalse, commandIsActive, invertedWording);
        this.commandTrue = new CommandSequence(
                commandTrue,
                Finder.killall()
        );
        this.commandFalse = new CommandSequence(
                commandFalse,
                Finder.killall()
        );
    }

}
