from __future__ import annotations


def install_customtkinter_compat() -> None:
    """Keep ULTRON compatible with newer CustomTkinter geometry validation.

    Newer CustomTkinter versions reject width/height passed to .place().
    Older ULTRON UI code uses that pattern in a few places. Move those values
    into widget configuration before delegating to the original .place().
    """
    try:
        from customtkinter.windows.widgets.core_widget_classes.ctk_base_class import CTkBaseClass
    except Exception:
        return

    if getattr(CTkBaseClass, "_ultron_place_compat_installed", False):
        return

    original_place = CTkBaseClass.place

    def compatible_place(self, *args, **kwargs):
        size = {}
        for key in ("width", "height"):
            if key in kwargs:
                size[key] = kwargs.pop(key)
        if size:
            try:
                self.configure(**size)
            except Exception:
                pass
        return original_place(self, *args, **kwargs)

    CTkBaseClass.place = compatible_place
    CTkBaseClass._ultron_place_compat_installed = True
