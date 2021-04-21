from .render_functions import RenderFunctions

class BasicRenderFunctions(RenderFunctions):
    def ternary(self, _input, a, b):
        return a if _input else b

    def get_functions(self):
        return {
            'ternary': self.ternary,
        }
