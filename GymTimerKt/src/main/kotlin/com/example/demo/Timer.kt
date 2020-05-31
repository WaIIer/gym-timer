package com.example.demo

import javafx.concurrent.Task
import java.time.Duration

class Timer(
        val durationSeconds: Long,
        val name: String
) {}

class TimerThread(private val durationSeconds: Long): Thread() {
    private var isPaused = false
    private var timeRemaining: Long = 0

    var onTimerUpdate: (Long) -> Unit = {t:Long -> print("$t\r")}

    override fun run() {
        val endTime = System.nanoTime() + secondsToNanos(durationSeconds)
        var count = 0

        while (!isPaused) {
            timeRemaining = endTime - System.nanoTime()
            if (timeRemaining <= 0) {
                timeRemaining = 0
                onTimerUpdate(timeRemaining)
                break
            }
            onTimerUpdate(timeRemaining)
            count++
        }
        println("Done: $count")
    }
}

fun secondsToNanos(seconds: Long): Long {
    return 1_000_000_000 * seconds
}