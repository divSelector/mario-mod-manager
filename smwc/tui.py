import urwid
from typing import List, Dict, Callable, Optional, Union

from .romhack import SMWRomhack
from .utils import update_stream_text

class SMWRomhackSelection(urwid.WidgetPlaceholder):
    max_box_levels = 4

    def __init__(self, queryset: List[Dict]) -> None:
        super(SMWRomhackSelection, self).__init__(urwid.SolidFill('.'))
        self.box_level = 0
        self.romhack: Optional[SMWRomhack] = None

        menu_items = [self.sub_menu(record['title'], [
            self.menu_button(sfc, self.item_chosen)
            for sfc in record['path']
        ]) for record in queryset]

        menu_top = self.menu(u'Select a Romhack', menu_items)

        self.open_box(menu_top)

    def open_box(self, box: urwid.Filler) -> None:
        self.original_widget: urwid.Overlay = urwid.Overlay(urwid.LineBox(box),
            self.original_widget,
            align='center', width=('relative', 80),
            valign='middle', height=('relative', 80),
            min_width=24, min_height=8,
            left=self.box_level * 3,
            right=(self.max_box_levels - self.box_level - 1) * 3,
            top=self.box_level * 2,
            bottom=(self.max_box_levels - self.box_level - 1) * 2)
        self.box_level += 1

    def keypress(self, size: int, key: str) -> None:
        if key == 'esc' and self.box_level > 1:
            self.original_widget = self.original_widget[0]
            self.box_level -= 1
        elif key == 'esc' and self.box_level == 1:
            self.exit()
        else:
            return super(SMWRomhackSelection, self).keypress(size, key)
        
    def menu_button(self, caption: Union[List[str], str], callback: Callable) -> urwid.AttrMap:
        button = urwid.Button(caption)
        urwid.connect_signal(button, 'click', callback)
        return urwid.AttrMap(button, None, focus_map='reversed')

    def sub_menu(self, caption: str, choices: List) -> urwid.AttrMap:
        contents = self.menu(caption, choices)
        def open_menu(button: urwid.Button) -> None:
            return self.open_box(contents)
        return self.menu_button([caption, u'...'], open_menu)

    def menu(self, title: str, choices: List) -> urwid.ListBox:
        body = [urwid.Text(title), urwid.Divider()]
        body.extend(choices)
        return urwid.ListBox(urwid.SimpleFocusListWalker(body))

    def item_chosen(self, button: urwid.Button) -> None:
        self.romhack = SMWRomhack(button.label)

        response = urwid.Text([
            f"ID:               {self.romhack.data[0]['id']}\n",
            f"Title:            {self.romhack.data[0]['title']}\n",
            f"Created On:       {self.romhack.data[0]['created_on']}\n",
            f"Page URL:         {self.romhack.data[0]['page_url']}\n",
            f"Is Demo:          {self.romhack.data[0]['is_demo']}\n",
            f"Is Featured:      {self.romhack.data[0]['is_featured']}\n",
            f"Exit Count:       {self.romhack.data[0]['exit_count']}\n",
            f"Exits Cleared:    {self.romhack.data[0]['exits_cleared']}\n",
            f"Rating:           {self.romhack.data[0]['rating']}\n",
            f"Size:             {self.romhack.data[0]['size']} {self.romhack.data[0]['size_units']}\n",
            f"Download Count:   {self.romhack.data[0]['downloaded_count']}\n",
            f"Type:             {self.romhack.data[0]['hack_type']}\n",
            f"Path:             {button.label}\n",
            f"Authors:          {self.romhack.data[0]['author']}\n",
        ])
        done = self.menu_button(u'Ok', self.launch)
        self.open_box(urwid.Filler(urwid.Pile([response, done])))

    def exit(self) -> None:
        raise urwid.ExitMainLoop()

    def launch(self, button: urwid.Button) -> None:
        if self.romhack is not None:
            self.romhack.launch_in_retroarch()
            self.exit()
        
