package main;

import settings.BooleanFinderSetting;
import settings.Setting;
import settings.commands.Command;
import ui.Frame;

import javax.swing.*;
import java.io.IOException;

/**
 * Created by jimneuendorf on 5/11/17.
 */
public class Main {
    public static final String APP_NAME = "AdvancedSettingsMacOS";

    /**
     * Run with -Xdock:name=AdvancesSettingsMacOS
     */
    public static void main(String[] args) {
        setSystemProperties();
        // Runtime rt = Runtime.getRuntime();
        //Process pr = rt.exec("java -jar map.jar time.rel test.txt debug");
        ProcessBuilder pb = new ProcessBuilder("defaults", "write", "com.apple.finder", "CreateDesktop", "-bool", "true");
        try {
            Process pr = pb.start();
        }
        catch (IOException e) {
            e.printStackTrace();
        }
        new Frame(APP_NAME, getSettings());
    }

    private static void setSystemProperties() {
        // take the menu bar off the jframe
        System.setProperty("apple.laf.useScreenMenuBar", "true");
        // set the name of the application menu item
        System.setProperty("com.apple.mrj.application.apple.menu.about.name", APP_NAME);
        // set the look and feel
        try {
            UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
        }
        catch (Exception e) {
            e.printStackTrace();
        }
    }

    private static Setting[] getSettings() {
        return new Setting[] {
                new BooleanFinderSetting(
                        "show desktop icons",
                        new Command("defaults", "write", "com.apple.finder", "CreateDesktop", "-bool", "true"),
                        new Command("defaults", "write", "com.apple.finder", "CreateDesktop", "-bool", "false"),
                        new Command("defaults", "read", "com.apple.finder", "CreateDesktop")
                ),
                new BooleanFinderSetting(
                        "Finder has Quit menu item",
                        new Command("defaults", "write", "com.apple.finder", "QuitMenuItem", "-bool", "true"),
                        new Command("defaults", "write", "com.apple.finder", "QuitMenuItem", "-bool", "false"),
                        new Command("defaults", "read", "com.apple.finder", "QuitMenuItem")
                )
        };
    }
}
