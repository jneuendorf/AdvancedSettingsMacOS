package settings.commands;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

/**
 * Created by jimneuendorf on 6/10/17.
 */
public class CommandSequenceResult implements AbstractCommandResult {
    private List<AbstractCommandResult> results;

    public CommandSequenceResult() throws InterruptedException, IOException {
        this.results = new ArrayList<>();
    }

    public void add(AbstractCommandResult commandResult) {
        results.add(commandResult);
    }

    @Override
    public String getOutput() {
        String output = "";
        for (AbstractCommandResult result : results) {
            output += result.getOutput();
        }
        return output;
    }

    @Override
    public boolean wasSuccessful() {
        for (AbstractCommandResult result : results) {
            if (!result.wasSuccessful()) {
                return false;
            }
        }
        return true;
    }
}
