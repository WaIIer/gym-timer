package tests

import com.example.demo.TimerThread


fun main(args: Array<String>) {
    val timerThread = TimerThread(10)
    timerThread.run()
    timerThread.join()
}
