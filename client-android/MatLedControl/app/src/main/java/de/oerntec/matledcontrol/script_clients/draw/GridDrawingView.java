package de.oerntec.matledcontrol.script_clients.draw;

import android.content.Context;
import android.graphics.Color;
import android.support.annotation.ColorInt;
import android.util.AttributeSet;
import android.view.View;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.Path;
import android.view.MotionEvent;

/**
 * see https://code.tutsplus.com/tutorials/android-sdk-create-a-drawing-app-touch-interaction--mobile-19202 for more information
 */
public class GridDrawingView extends View {
    /**
     * drawing path
     */
    private Path drawPath;

    /**
     * drawing and canvas paint
     */
    private Paint drawPaint, canvasPaint;

    /**
     * canvas
     */
    private Canvas drawCanvas;

    /**
     * canvas bitmap
     */
    private Bitmap canvasBitmap;

    @ColorInt private int mDrawingColor = Color.BLACK;

    private Grid mGrid;

    public GridDrawingView(Context context, AttributeSet attrs) {
        super(context, attrs);

        drawPath = new Path();
        drawPaint = new Paint();

        drawPaint.setAntiAlias(true);
        drawPaint.setStrokeWidth(20);
        drawPaint.setStyle(Paint.Style.STROKE);
        drawPaint.setStrokeJoin(Paint.Join.ROUND);
        drawPaint.setStrokeCap(Paint.Cap.ROUND);
        drawPaint.setColor(mDrawingColor);

        canvasPaint = new Paint(Paint.DITHER_FLAG);
    }

    @ColorInt int getColor() {
        return mDrawingColor;
    }

    void setColor(@ColorInt int color) {
        mDrawingColor = color;
    }

    void setGridSize(int width, int height) {
        mGrid = new Grid(drawPaint, getWidth(), getHeight(), width, height);
    }

    @Override
    protected void onSizeChanged(int w, int h, int oldw, int oldh) {
        super.onSizeChanged(w, h, oldw, oldh);

        canvasBitmap = Bitmap.createBitmap(w, h, Bitmap.Config.ARGB_8888);
        drawCanvas = new Canvas(canvasBitmap);

        if(mGrid != null)
            mGrid.setCanvasSize(w, h);
    }

    @Override
    protected void onDraw(Canvas canvas) {
        canvas.drawBitmap(canvasBitmap, 0, 0, canvasPaint);
        if(mGrid != null)
            mGrid.draw(canvas);
    }

    @Override
    public boolean onTouchEvent(MotionEvent event) {
        mGrid.setColor(Math.round(event.getX()), Math.round(event.getY()), mDrawingColor);
        invalidate();
        return true;
    }

    private class Grid {
        private final Cell[][] mGrid;
        private final Paint mPaint;
        private static final int GRID_LINE_WIDTH = 5;
        private final int mHorizontalCellCount, mVerticalCellCount;

        Grid(Paint paint, int width, int height, int horizontalCellCount, int verticalCellCount) {
            mPaint = paint;
            mHorizontalCellCount = horizontalCellCount;
            mVerticalCellCount = verticalCellCount;

            mGrid = new Cell[horizontalCellCount][verticalCellCount];
            recreateCells(width, height);
        }

        private void recreateCells(int width, int height) {
            int cellWidth = (width - ((mHorizontalCellCount - 1) * GRID_LINE_WIDTH)) / mHorizontalCellCount;
            int cellHeight = (height - ((mVerticalCellCount - 1) * GRID_LINE_WIDTH)) / mVerticalCellCount;

            int cellWidthWithBorder = cellWidth + GRID_LINE_WIDTH;
            int cellHeightWithBorder = cellHeight + GRID_LINE_WIDTH;

            for(int x = 0; x < mHorizontalCellCount; x++) {
                for (int y = 0; y < mVerticalCellCount; y++) {
                    mGrid[x][y] = new Cell(cellWidth, cellHeight, x * cellWidthWithBorder, y * cellHeightWithBorder);
                }
            }
        }

        void draw(Canvas canvas) {
            Paint.Style oldStyle = mPaint.getStyle();
            mPaint.setStyle(Paint.Style.FILL);
            for(int x = 0; x < mGrid.length; x++) {
                for (int y = 0; y < mGrid[0].length; y++) {
                    mGrid[x][y].draw(canvas, mPaint);
                }
            }
            mPaint.setStyle(oldStyle);
        }

        void setColor(int x, int y, @ColorInt int color) {
            for(int i = 0; i < mGrid.length; i++) {
                for (int j = 0; j < mGrid[0].length; j++) {
                    if(mGrid[i][j].contains(x, y))
                        mGrid[i][j].setColor(color);
                }
            }
        }

        void setCanvasSize(int w, int h) {
            recreateCells(w, h);
        }

        private class Cell {
            private int width, height, x, y;

            @ColorInt
            int color;

            Cell(int width, int height, int x, int y, int color) {
                this.width = width;
                this.height = height;
                this.x = x;
                this.y = y;
                this.color = color;
            }

            Cell(int width, int height, int x, int y) {
                this(width, height, x, y, Color.BLACK);
            }

            boolean contains(int pX, int pY) {
                return pX >= x && pX < x + width && pY >= y && pY < y + height;
            }

            void setColor(@ColorInt int color) {
                this.color = color;
            }

            void draw(Canvas canvas, Paint paint) {
                paint.setColor(color);
                canvas.drawRect(x, y, x + width, y + height, paint);
            }
        }
    }
}
