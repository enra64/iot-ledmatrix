package de.oerntec.matledcontrol;

import android.app.Activity;
import android.app.ApplicationErrorReport;
import android.content.Context;
import android.content.Intent;

import java.io.PrintWriter;
import java.io.StringWriter;

/**
 * Created by arne on 25.12.17.
 */

public class FeedbackSender {
    /**
     * Send feedback using the android feedback mechanism
     *
     * @param activity required for package info and starting the intent
     * @param e the exception to report on
     */
    public static void sendFeedback(Activity activity, Exception e) {
        ApplicationErrorReport report = new ApplicationErrorReport();
        report.packageName = report.processName = activity.getApplication()
                .getPackageName();
        report.time = System.currentTimeMillis();
        report.type = ApplicationErrorReport.TYPE_CRASH;
        report.systemApp = false;

        ApplicationErrorReport.CrashInfo crash = new ApplicationErrorReport.CrashInfo();
        crash.exceptionClassName = e.getClass().getSimpleName();
        crash.exceptionMessage = e.getMessage();

        StringWriter writer = new StringWriter();
        PrintWriter printer = new PrintWriter(writer);
        e.printStackTrace(printer);

        crash.stackTrace = writer.toString();

        StackTraceElement stack = e.getStackTrace()[0];
        crash.throwClassName = stack.getClassName();
        crash.throwFileName = stack.getFileName();
        crash.throwLineNumber = stack.getLineNumber();
        crash.throwMethodName = stack.getMethodName();

        report.crashInfo = crash;

        String packageName = "com.google.android.feedback";
        String className = "com.google.android.feedback.FeedbackActivity";

        Intent intent = new Intent(Intent.ACTION_APP_ERROR);
        intent.putExtra(Intent.EXTRA_BUG_REPORT, report);
        intent.setClassName(packageName, className);  // To avoid the dialog to select the feedback tool

        activity.startActivity(intent);
    }
}
