package settings.commands;

import java.io.IOException;

/**
 * Created by jimneuendorf on 6/8/17.
 */
public class Command implements RunnableCommand {
    private String[] commands;

    public Command(String... commands) {
        this.commands = commands;
    }

    public static CommandResult run(String... command) throws IOException, InterruptedException {
        ProcessBuilder pb = new ProcessBuilder(command);
        System.out.println("running command: " + String.join(" ", command));
        return new CommandResult(pb.start());

    }

    @Override
    public AbstractCommandResult run() throws Exception {
        return Command.run(commands);
    }
}
