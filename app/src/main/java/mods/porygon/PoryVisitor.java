package mods.porygon;

import javax.imageio.ImageIO;
import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.IOException;
import java.nio.file.FileVisitResult;
import java.nio.file.FileVisitor;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.attribute.BasicFileAttributes;

public class PoryVisitor implements FileVisitor<Path> {
    private final String output;

    public PoryVisitor(String output) {
        this.output = output;
    }


    @Override
    public FileVisitResult preVisitDirectory(Path dir, BasicFileAttributes attrs) throws IOException {
        return FileVisitResult.CONTINUE;
    }

    @Override
    public FileVisitResult visitFile(Path path, BasicFileAttributes attrs) throws IOException {
        BufferedImage original = ImageIO.read(path.toFile());
        int width = original.getWidth() * 2, height = original.getHeight() * 2;
        int type = original.getType();
        System.out.println(path);
        System.out.println(type);
        //todo fix type
        if (type == 0) {
            if (original.getAlphaRaster() == null) {
                type = BufferedImage.TYPE_INT_RGB;
            } else {
                type = BufferedImage.TYPE_INT_ARGB;
            }
        }
        BufferedImage resized = new BufferedImage(width, height, type);
        Graphics2D canvas = resized.createGraphics();
        //todo renderinghints
        canvas.drawImage(original, 0, 0, width, height, null);
        canvas.dispose();
        ImageIO.write(resized, "JPEG", Paths.get(this.output, path.getFileName().toString().split("\\.")[0] + ".jpg").toFile());
        return FileVisitResult.CONTINUE;
    }

    @Override
    public FileVisitResult visitFileFailed(Path path, IOException exc) throws IOException {
        return FileVisitResult.CONTINUE;
    }

    @Override
    public FileVisitResult postVisitDirectory(Path dir, IOException exc) throws IOException {
        return FileVisitResult.CONTINUE;
    }
}
