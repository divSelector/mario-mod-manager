import urwid
from typing import List, Dict

from .romhack import SMWRomhack


class SMWRomhackSelection(urwid.WidgetPlaceholder):
    max_box_levels = 4

    def __init__(self, queryset: List[Dict]):
        super(SMWRomhackSelection, self).__init__(urwid.SolidFill('M'))
        self.box_level = 0
        self.romhack = None

        menu_items = [self.sub_menu(record['title'], [

            self.menu_button(sfc, self.item_chosen)
            for sfc in record['path']

        ]) for record in queryset]

        menu_top = self.menu(u'Select a Romhack', menu_items)

        self.open_box(menu_top)

    def open_box(self, box):
        self.original_widget = urwid.Overlay(urwid.LineBox(box),
            self.original_widget,
            align='center', width=('relative', 80),
            valign='middle', height=('relative', 80),
            min_width=24, min_height=8,
            left=self.box_level * 3,
            right=(self.max_box_levels - self.box_level - 1) * 3,
            top=self.box_level * 2,
            bottom=(self.max_box_levels - self.box_level - 1) * 2)
        self.box_level += 1

    def keypress(self, size, key):
        if key == 'esc' and self.box_level > 1:
            self.original_widget = self.original_widget[0]
            self.box_level -= 1
        else:
            return super(SMWRomhackSelection, self).keypress(size, key)
        
    def menu_button(self, caption, callback):
        button = urwid.Button(caption)
        urwid.connect_signal(button, 'click', callback)
        return urwid.AttrMap(button, None, focus_map='reversed')

    def sub_menu(self, caption, choices):
        contents = self.menu(caption, choices)
        def open_menu(button):
            return self.open_box(contents)
        return self.menu_button([caption, u'...'], open_menu)

    def menu(self, title, choices):
        body = [urwid.Text(title), urwid.Divider()]
        body.extend(choices)
        return urwid.ListBox(urwid.SimpleFocusListWalker(body))

    def item_chosen(self, button):
        self.romhack = SMWRomhack(button.label)
        response = urwid.Text([u'You chose ', button.label, u'\n'])
        done = self.menu_button(u'Ok', self.launch_and_exit)
        self.open_box(urwid.Filler(urwid.Pile([response, done])))

    def exit_program(self):
        raise urwid.ExitMainLoop()

    def launch_and_exit(self, button):
        self.romhack.launch_in_retroarch()
        self.exit_program()
        

# main_box = SMWRomhackSelection()