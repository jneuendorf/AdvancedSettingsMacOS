package ui;

import settings.Setting;

import javax.swing.*;
import java.awt.*;

/**
 * Created by jimneuendorf on 5/12/17.
 */
public class Frame extends JFrame {

    public Frame(String title, Setting... settings) {
        super(title);
        setDefaultCloseOperation(WindowConstants.EXIT_ON_CLOSE);
        //setPreferredSize(FRAME_DIMENSION);
        //setMinimumSize(new Dimension(600, 400));
        // center the window
        setLocationRelativeTo(null);
        //setResizable(false);
        buildGui(settings);
        displayFrame();
    }

    public void displayFrame() {
        pack();
        setVisible(true);
    }

    public void buildGui(Setting[] settings) {
        Container pane = getContentPane();
        //pane.setLayout(new BoxLayout(pane, BoxLayout.X_AXIS));
        pane.setLayout(new GridLayout(0, 3));

        for (Setting setting : settings) {
            pane.add(setting.createComponent());
        }

        //graphContainer = new JPanel();
        //graphContainer.setLayout(new BoxLayout(graphContainer, BoxLayout.X_AXIS));
        //graphContainer.setPreferredSize(FRAME_DIMENSION_HALF);
        //pane.add(graphContainer);
        //renderGraph(graphContainer);
        //
        //settingsContainer = new JPanel();
        //settingsContainer.setLayout(new BoxLayout(settingsContainer, BoxLayout.Y_AXIS));
        //settingsContainer.setPreferredSize(FRAME_DIMENSION_HALF);
        //pane.add(settingsContainer);
        //renderForm(settingsContainer);
    }
}
