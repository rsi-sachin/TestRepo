package com.tts.demo.util;

import java.io.ByteArrayInputStream;
import java.io.InputStream;
import java.io.OutputStream;

/**
 * Mock Process implementation for testing JTL file tailing behavior.
 * Allows controlled simulation of process lifecycle (alive/terminated) on a schedule.
 */
public class MockProcess extends Process {
    
    private final long aliveDurationMs;
    private final long startTime;
    private boolean destroyed;
    private int exitValue;

    /**
     * Create a mock process that will be "alive" for the specified duration.
     * 
     * @param aliveDurationMs How long the process should report isAlive() = true (milliseconds)
     */
    public MockProcess(long aliveDurationMs) {
        this(aliveDurationMs, 0);
    }

    /**
     * Create a mock process with specified alive duration and exit code.
     * 
     * @param aliveDurationMs How long the process should report isAlive() = true (milliseconds)
     * @param exitValue Exit code to return when process terminates
     */
    public MockProcess(long aliveDurationMs, int exitValue) {
        this.aliveDurationMs = aliveDurationMs;
        this.startTime = System.currentTimeMillis();
        this.destroyed = false;
        this.exitValue = exitValue;
    }

    @Override
    public OutputStream getOutputStream() {
        return OutputStream.nullOutputStream();
    }

    @Override
    public InputStream getInputStream() {
        return new ByteArrayInputStream(new byte[0]);
    }

    @Override
    public InputStream getErrorStream() {
        return new ByteArrayInputStream(new byte[0]);
    }

    @Override
    public int waitFor() throws InterruptedException {
        while (isAlive()) {
            Thread.sleep(50);
        }
        return exitValue;
    }

    @Override
    public int exitValue() {
        if (isAlive()) {
            throw new IllegalThreadStateException("Process has not exited");
        }
        return exitValue;
    }

    @Override
    public void destroy() {
        destroyed = true;
    }

    @Override
    public boolean isAlive() {
        if (destroyed) {
            return false;
        }
        long elapsed = System.currentTimeMillis() - startTime;
        return elapsed < aliveDurationMs;
    }

    /**
     * Manually terminate the process (for testing early termination scenarios).
     */
    public void terminate() {
        destroyed = true;
    }

    /**
     * Set the exit value (useful for testing different exit scenarios).
     */
    public void setExitValue(int exitValue) {
        this.exitValue = exitValue;
    }
}
