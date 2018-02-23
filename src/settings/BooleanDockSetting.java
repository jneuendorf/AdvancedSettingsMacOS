package settings;

import settings.commands.CommandSequence;
import settings.commands.RunnableCommand;

/**
 * Created by jimneuendorf on 6/10/17.
 */
public class BooleanDockSetting extends BooleanSetting {

    public BooleanDockSetting(String name, RunnableCommand commandTrue, RunnableCommand commandFalse, RunnableCommand commandIsActive, boolean invertedWording) {
        super(name, commandTrue, commandFalse, commandIsActive, invertedWording);
        this.commandTrue = new CommandSequence(
                commandTrue,
                Dock.killall()
        );
        this.commandFalse = new CommandSequence(
                commandFalse,
                Dock.killall()
        );
    }

    public BooleanDockSetting(String name, RunnableCommand commandTrue, RunnableCommand commandFalse, RunnableCommand commandIsActive) {
        this(name, commandTrue, commandFalse, commandIsActive, false);
    }

}
