package settings.commands;

import java.util.ArrayList;
import java.util.Arrays;

/**
 * Created by jimneuendorf on 6/9/17.
 */
public class CommandSequence extends ArrayList<RunnableCommand> implements RunnableCommand {

    public CommandSequence(RunnableCommand... commands) {
        super(Arrays.asList(commands));
    }

    @Override
    public CommandSequenceResult run() throws Exception {
        CommandSequenceResult commandResult = new CommandSequenceResult();
        for (RunnableCommand command : this) {
            commandResult.add(command.run());
        }
        return commandResult;
    }

}
