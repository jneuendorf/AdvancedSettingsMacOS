package settings.commands;

/**
 * Created by jimneuendorf on 6/10/17.
 */
public interface AbstractCommandResult {
    String getOutput();

    boolean wasSuccessful();
}
