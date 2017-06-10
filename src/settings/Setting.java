package settings;

import javax.swing.*;

/**
 * Created by jimneuendorf on 6/9/17.
 */
public abstract class Setting {
    private String name;

    public Setting(String name) {
        this.name = name;
    }

    abstract public JComponent createComponent();

    public String getName() {
        return name;
    }

}
