package settings;

import settings.commands.RunnableCommand;

import javax.swing.*;
import java.awt.event.ItemEvent;

/**
 * Created by jimneuendorf on 6/10/17.
 */
public class BooleanSetting extends Setting {
    RunnableCommand commandTrue;
    RunnableCommand commandFalse;
    RunnableCommand commandIsActive;
    boolean invertedWording;

    public BooleanSetting(String name, RunnableCommand commandTrue, RunnableCommand commandFalse, RunnableCommand commandIsActive) {
        this(name, commandTrue, commandFalse, commandIsActive, false);
    }

    public BooleanSetting(String name, RunnableCommand commandTrue, RunnableCommand commandFalse, RunnableCommand commandIsActive, boolean invertedWording) {
        super(name);
        this.commandTrue = commandTrue;
        this.commandFalse = commandFalse;
        this.commandIsActive = commandIsActive;
        this.invertedWording = invertedWording;
    }

    public boolean isActive() {
        boolean result = getState();
        //System.out.println("BooleanSetting::state:" + result);
        if (invertedWording) {
            result = !result;
        }
        //System.out.println("BooleanSetting::isActive:" + result);
        return result;
    }

    @Override
    public JComponent createComponent() {
        JCheckBox box = new JCheckBox(getName(), isActive());
        box.addItemListener(event -> {
            try {
                if (event.getStateChange() == ItemEvent.SELECTED) {
                    System.out.println(commandTrue.run());
                }
                else {
                    System.out.println(commandFalse.run());
                }
            }
            catch (Exception e) {
                e.printStackTrace();
            }
        });
        return box;
    }

    private boolean getState() {
        String result;
        try {
            result = commandIsActive.run().getOutput();
        }
        catch (Exception e) {
            System.out.println(e.getMessage());
            result = "0";
        }
        switch (result.trim()) {
            case "1":
                return true;
        }
        return false;
    }
}
