package mods.porygon;
import javax.imageio.ImageIO;
import javax.swing.*;
import java.awt.*;

import java.awt.event.ActionEvent;
import java.io.File;
import java.io.IOException;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Paths;

public class Porygon extends JFrame {
    protected JTextField inputDir, outputDir, filter;

    public Porygon() {
        super("Porygon");
        try {
            UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
            URL res = this.getClass().getResource("/icon.png");
            if (res != null) this.setIconImage(ImageIO.read(res));
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            this.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
            this.inputDir = new JTextField(16);
            this.outputDir = new JTextField(16);
            this.filter = new JTextField("*");
        }
    }

    public static void main(String[] args) {
        //SwingUtilities.invokeLater(() -> {
        Porygon frame = new Porygon();

        GridBagLayout layout = new GridBagLayout();
        frame.setLayout(layout);
        GridBagConstraints c = new GridBagConstraints();
        c.fill = GridBagConstraints.BOTH;
        c.gridy = 0;
        frame.addLabelFieldCombo("Input Directory", c, frame.inputDir, true);
        c.gridy++;
        frame.addLabelFieldCombo("Output Directory", c, frame.outputDir, true);
        c.gridy++;
        frame.addLabelFieldCombo("Filter", c, frame.filter, false);
        c.gridy++;
        frame.addProcessingButton(c);
        frame.pack();
        frame.resize();
        frame.setVisible(true);
        //});
    }

    protected void resize() {
        Rectangle bounds = this.getGraphicsConfiguration().getDevice().getDefaultConfiguration().getBounds();
        int x = bounds.width - this.getWidth() >> 1;
        int y = bounds.height - this.getHeight() >> 1;
        this.setLocation(x, y);
    }

    protected void addLabelFieldCombo(String desc, GridBagConstraints c, JTextField textField, boolean hasButton) {
        c.ipadx = 15;
        this.add(new JLabel(desc, SwingConstants.CENTER), c);
        c.ipadx = 0;
        if (hasButton) {
            c.gridwidth = 1;
            this.add(textField, c);
            JButton butt = new JButton("...");
            butt.addActionListener(event -> {
                JFileChooser fc = new JFileChooser();
                fc.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY);
                fc.setAcceptAllFileFilterUsed(false);
                int res = fc.showOpenDialog(this);
                if (res == JFileChooser.APPROVE_OPTION) {
                    File file = fc.getSelectedFile();
                    textField.setText(file.toString());
                }
            });
            this.add(butt, c);
        } else {
            c.gridwidth = 2;
            this.add(textField, c);
        }
    }

    protected void addProcessingButton(GridBagConstraints c) {
        c.gridwidth = 3;
        c.insets.top = 20;
        c.fill = GridBagConstraints.NONE;
        c.ipady = 0;
        JButton button = new JButton("Commence");
        button.addActionListener(this::processFiles);
        this.add(button, c);
    }

    protected void processFiles(ActionEvent e) {
        try {
            Files.walkFileTree(Paths.get(this.inputDir.getText()), new PoryVisitor(this.outputDir.getText()));
        } catch (IOException ex) {
            ex.printStackTrace();
        }
    }
}
