package de.oerntec.matledcontrol.script_clients.draw;

import android.content.Context;
import android.graphics.Color;
import android.support.annotation.ColorInt;
import android.util.AttributeSet;
import android.view.View;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.view.MotionEvent;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

/**
 * see https://code.tutsplus.com/tutorials/android-sdk-create-a-drawing-app-touch-interaction--mobile-19202 for more information
 */
public class GridDrawingView extends View {

    /**
     * drawing and canvas paint
     */
    private Paint drawPaint, canvasPaint;

    /**
     * canvas bitmap
     */
    private Bitmap canvasBitmap;

    /**
     * The color currently selected by the user
     */
    @ColorInt
    private int mDrawingColor = Color.BLACK;

    /**
     * Contains all color information for cells
     */
    private Grid mGrid;

    private GridChangeListener mGridChangeListener = null;

    /**
     * Create a new GridDrawingView
     */
    public GridDrawingView(Context context, AttributeSet attrs) {
        super(context, attrs);

        // initialise the paint we use for drawing
        drawPaint = new Paint();
        drawPaint.setAntiAlias(true);
        drawPaint.setStrokeWidth(20);
        drawPaint.setStyle(Paint.Style.STROKE);
        drawPaint.setStrokeJoin(Paint.Join.ROUND);
        drawPaint.setStrokeCap(Paint.Cap.ROUND);
        drawPaint.setColor(mDrawingColor);

        // the paint we use for the background
        canvasPaint = new Paint(Paint.DITHER_FLAG);
        canvasPaint.setColor(Color.WHITE);
    }

    /**
     * Retrieve the currently selected color. Any color updates (fx by tapping a cell) will use this color.
     */
    @ColorInt
    int getColor() {
        return mDrawingColor;
    }

    /**
     * Change the color used for drawing any changes from this point on
     *
     * @param color color to be used
     */
    void setColor(@ColorInt int color) {
        mDrawingColor = color;
    }

    void setGridChangeListener(GridChangeListener listener) {
        mGridChangeListener = listener;
    }

    /**
     * Set the grid size this widget should use (_not_ the number of pixels this view has)
     */
    void setGridSize(int width, int height) {
        mGrid = new Grid(drawPaint, getWidth(), getHeight(), width, height);
    }

    /**
     * Called whenever this widget changes size
     */
    @Override
    protected void onSizeChanged(int w, int h, int oldw, int oldh) {
        super.onSizeChanged(w, h, oldw, oldh);

        canvasBitmap = Bitmap.createBitmap(w, h, Bitmap.Config.ARGB_8888);

        if (mGrid != null)
            mGrid.setCanvasSize(w, h);
    }

    @Override
    protected void onDraw(Canvas canvas) {
        canvas.drawBitmap(canvasBitmap, 0, 0, canvasPaint);
        if (mGrid != null)
            mGrid.draw(canvas);
    }

    @Override
    public boolean onTouchEvent(MotionEvent event) {
        if(mGrid.onTouch(Math.round(event.getX()), Math.round(event.getY()), mDrawingColor))
            mGridChangeListener.onGridChanged();

        invalidate();
        return true;
    }

    public JSONObject getGridAsJsonObject() {
        try {
            return mGrid.toJsonObject();
        } catch (JSONException e) {
            e.printStackTrace();
            return null;
        }
    }

    /**
     * Class containing all cells.
     */
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

            for (int x = 0; x < mHorizontalCellCount; x++) {
                for (int y = 0; y < mVerticalCellCount; y++) {
                    mGrid[x][y] = new Cell(cellWidth, cellHeight, x * cellWidthWithBorder, y * cellHeightWithBorder);
                }
            }
        }

        void draw(Canvas canvas) {
            Paint.Style oldStyle = mPaint.getStyle();
            mPaint.setStyle(Paint.Style.FILL);
            for (int x = 0; x < mGrid.length; x++) {
                for (int y = 0; y < mGrid[0].length; y++) {
                    mGrid[x][y].draw(canvas, mPaint);
                }
            }
            mPaint.setStyle(oldStyle);
        }

        /**
         * Update the color of the cell at the touched location
         * @return true if a value changed, false otherwise
         */
        boolean onTouch(int touch_x, int touch_y, @ColorInt int color) {
            boolean hasChanged = false;
            for (int x = 0; x < mGrid.length; x++) {
                for (int y = 0; y < mGrid[0].length; y++) {
                    if (mGrid[x][y].contains(touch_x, touch_y)){
                        if (mGrid[x][y].getColor() != color)
                            hasChanged = true;

                        mGrid[x][y].setColor(color);
                    }
                }
            }
            return hasChanged;
        }

        JSONObject toJsonObject() throws JSONException {
            JSONArray array = new JSONArray();
            for (int x = 0; x < mGrid.length; x++) {
                JSONArray columnArray = new JSONArray();
                for (int y = 0; y < mGrid[0].length; y++) {
                    JSONArray colorArray = new JSONArray();
                    colorArray.put(Color.red(mGrid[x][y].color));
                    colorArray.put(Color.green(mGrid[x][y].color));
                    colorArray.put(Color.blue(mGrid[x][y].color));
                    columnArray.put(colorArray);
                }
                array.put(columnArray);
            }
            JSONObject wrapper = new JSONObject();
            wrapper.put("color_array", array);
            return wrapper;
        }

        /**
         * Set the size of the canvas (_not_ the grid size)
         * @param w width in pixels
         * @param h height in pixels
         */
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

            @ColorInt int getColor() {
                return this.color;
            }

            void draw(Canvas canvas, Paint paint) {
                paint.setColor(color);
                canvas.drawRect(x, y, x + width, y + height, paint);
            }
        }
    }

    interface GridChangeListener {
        void onGridChanged();
    }
}
