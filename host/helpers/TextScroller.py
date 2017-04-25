from Canvas import Canvas
from CustomScript import CustomScript
from helpers.Color import Color


class TextScroller:
    """
    This class is designed to help with scrolling text over the canvas. Following functions are expected to be forwarded:
    * :meth:`update` to update the text position
    * :meth:`draw` to draw the text. background can be cleared.
    
    The following functions may be called to change the text:
    * :meth:`set_text` change displayed text
    * :meth:`set_font` change font the text is rendered in
    * :meth:`set_size` change font size
    * :meth:`set_color` change text color
    """

    def __init__(self, canvas, text: str = None, font_path="Inconsolata.otf", font_size: int = 10):
        self.current_x = 0
        self.current_y = 0
        self.current_color = Color(255, 255, 255)

        self.canvas = canvas
        self.font_path = font_path
        self.font_size = font_size

        self.current_text_width = None
        self.rendered_text = None
        self.text = text

        self.re_render = text is not None

    def set_text(self, text: str):
        """
        Change the displayed text. Position will be reset.
        
        :param text: the new text
        """
        self.text = text
        self.current_x = self.canvas.width
        self.re_render = True

    def set_font(self, font_path: str):
        """
        Change the font used for the display.
        
        :param font_path: path to the font file
        """
        self.re_render = True
        self.font_path = font_path

    def set_size(self, font_size: int):
        """
        Change font size
        
        :param font_size: font size. 13 is large
        """
        self.font_size = font_size
        self.re_render = True

    def set_color(self, color: Color):
        """
        Change text color
        
        :param color: text color
        """
        self.current_color = color

    def update(self):
        """
        Update the font display
        """
        self.current_x -= 1

        if self.re_render and self.text is not None and self.font_path is not None and self.font_size is not None:
            self.re_render = False
            self.rendered_text = self.canvas.render_text(self.text, self.font_path, self.font_size)

        # wrap around matrix borders
        if self.rendered_text is not None and self.current_text_width is not None:
            if self.current_x + self.current_text_width < 0:
                self.current_x = self.canvas.width

    def draw(self, canvas: Canvas, clear: bool = False):
        """
        Draw the font pixels to the screen.
        
        :param canvas: the canvas to be drawn to 
        :param clear: if True, the canvas will be cleared before drawing the font
        """
        if clear:
            canvas.clear()
        if self.rendered_text is not None:
            self.current_text_width = canvas.draw_text(self.rendered_text, int(self.current_x), int(self.current_y), self.current_color)
