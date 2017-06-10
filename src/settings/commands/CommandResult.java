package settings.commands;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

/**
 * Created by jimneuendorf on 6/10/17.
 */
public class CommandResult implements AbstractCommandResult {
    private int exitValue;
    private String output;

    /**
     * The constuctur returns when the process has finished.
     * @param process The started process.
     */
    public CommandResult(Process process) throws InterruptedException, IOException {
        this.exitValue = process.waitFor();
        this.output = processOutputToString(process);
    }

    private String processOutputToString(Process process) throws IOException {
        BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
        StringBuilder builder = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            builder.append(line);
            builder.append(System.getProperty("line.separator"));
        }
        return builder.toString();
    }

    @Override
    public String getOutput() {
        return output;
    }

    @Override
    public boolean wasSuccessful() {
        return exitValue == 0;
    }
}
