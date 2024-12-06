#! /bin/python

# This script is used to generate a quick summary about the most frequently used commands and files in the bash history file.
# Usage: python cli_wrapped.py

from collections import Counter
import os
import shlex
from colorama import init, Fore, Style
import re

init(autoreset=True)

# Define color schemes
COMMAND_COLOR = Fore.GREEN + Style.BRIGHT        
FILLED_BAR_COLOR = Fore.GREEN + Style.BRIGHT    
UNFILLED_BAR_COLOR = Fore.RED + Style.DIM       
FILE_COLOR = Fore.GREEN + Style.BRIGHT           
THEME_COLOR = Fore.YELLOW + Style.BRIGHT    

class CliWrap:
    def __init__(self):
        self.history_file = os.path.expanduser("~/.bash_history")
        self.box_width = 95
        self.output = []
        self.commands = []
        self.command_count = {}
        self.total_commands = 0

        if not os.path.exists(self.history_file):
            warning_message = THEME_COLOR + "Warning: .bash_history file not found."
            self.output.append(warning_message)
            print('\n'.join(self.output))
            exit(1)

        with open(self.history_file, "r") as f:
            self.commands = f.readlines()

    def strip_ansi_codes(self, text):
        ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
        return ansi_escape.sub('', text)

    def truncate_text(self, text, max_visible_length):
        visible_length = 0
        result = ''
        ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
        matches = list(ansi_escape.finditer(text))
        index = 0
        truncated = False
        while index < len(text):
            if matches and index == matches[0].start():
                result += matches[0].group()
                index = matches[0].end()
                matches.pop(0)
            else:
                if visible_length < max_visible_length:
                    result += text[index]
                    visible_length += 1
                    index += 1
                else:
                    truncated = True
                    break
        if truncated:
            result += '...'
            visible_length += 3
        return result

    def create_outer_box(self, content_lines, width):
        border_top = '┌┌' + '─' * (width - 2) + '┐┐'
        border_bottom = '└└' + '─' * (width - 2) + '┘┘'
        boxed_content = [THEME_COLOR + border_top]
        for line in content_lines:
            for subline in line.split('\n'):
                subline = subline.rstrip()
                content_width = width - 4
                subline = self.truncate_text(subline, content_width)
                visible_length = len(self.strip_ansi_codes(subline))
                padding_length = content_width - visible_length
                padded_subline = subline + ' ' * padding_length
                boxed_content.append(THEME_COLOR + f"││ {padded_subline}{THEME_COLOR} ││")
        boxed_content.append(THEME_COLOR + border_bottom)
        return boxed_content

    def pad_text(self, text, color, width):
        text = self.truncate_text(text, width)
        return color + text.ljust(width) + Style.RESET_ALL
    
    def count_item_frequencies(self, item: list):
        item_count = Counter(item)
        total_items = sum(item_count.values())
        top_items = item_count.most_common(10)
        item_percentages = []
        for cmd, count in top_items:
            percentage = (count / total_items) * 100
            item_percentages.append((cmd, percentage))

        return total_items, item_percentages
    
    def create_scaled_bar(self, percentage, bar_length=30):
        filled_length = int(round(bar_length * percentage / 100)) + 7
        filled_length = min(filled_length, bar_length)  
        filled_part = FILLED_BAR_COLOR + '█' * filled_length + Style.RESET_ALL
        unfilled_part = UNFILLED_BAR_COLOR + '-' * (bar_length - filled_length) + Style.RESET_ALL
        bar = filled_part + unfilled_part
        return bar
    
    def present_top_items(self, items:list[tuple], color = FILE_COLOR,):
        for i, (item, perc) in enumerate(items):
            i += 1
            bar = self.create_scaled_bar(perc)
            padded_item = self.pad_text(f"{i}. {item}", color, 30)
            return (f"{padded_item:>50} | {bar} | {perc:5.1f}%") 

class Command(CliWrap):

    def __init__(self):
        super().__init__()

    def extract_commands(self):
        commands_list = [ cmd.strip() for cmd in self.commands ]
        return commands_list
    
class File(CliWrap):

    def __init__(self):
        super().__init__()

    def extract_files(self):
        file_pattern = re.compile(r'\b\w+\.\w{2}\b')
        files_list = []
        for cmd in self.commands:
            cmd = cmd.strip()
            if not cmd:
                continue
            try:
                words = shlex.split(cmd)
            except ValueError:
                continue
            for word in words:
                if file_pattern.match(word) and '/' not in word:
                    files_list.append(word)
        return files_list
    

def main():
    cli_wrap = CliWrap()
    command = Command()
    file = File()

    total_commands, command_percentages = command.count_item_frequencies(command.extract_commands())
    total_files, file_percentages = file.count_item_frequencies(file.extract_files())

    ascii_title = """
                                         
        *                    *                       *                 *              *
                 
  *  ██████╗██╗     ██╗    ██╗    ██╗██████╗  █████╗ ██████╗ ██████╗ ███████╗██████╗ *
    ██╔════╝██║     ██║    ██║    ██║██╔══██╗██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗
    ██║     ██║     ██║    ██║ █╗ ██║██████╔╝███████║██████╔╝██████╔╝█████╗  ██║  ██║
    ██║     ██║     ██║    ██║███╗██║██╔══██╗██╔══██║██╔═══╝ ██╔═══╝ ██╔══╝  ██║  ██║
    ╚██████╗███████╗██║    ╚███╔███╔╝██║  ██║██║  ██║██║     ██║     ███████╗██████╔╝
     ╚═════╝╚══════╝╚═╝     ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝     ╚══════╝╚═════╝                             
                                              
    *                    *██████╗  ██████╗ ██████╗ ██╗  ██╗
                          ╚════██╗██╔═████╗╚════██╗██║  ██║   *                     *
         *                █████╔╝ ██║██╔██║ █████╔╝███████║            
                          ██╔═══╝ ████╔╝██║██╔═══╝ ╚════██║
                          ███████╗╚██████╔╝███████╗     ██║                *
                 *    *   ╚══════╝ ╚═════╝ ╚══════╝     ╚═╝ *
     """.strip()
    
    cli_wrap.output.append(ascii_title)
    
    top_commands_title = """
__________________________________________________________________________________________
------------------------------------------------------------------------------------------
           _____               ___                                    _     
          |_   _|___  _ __    / __| ___  _ __   _ __   __ _  _ _   __| | ___
            | | / _ \\| '_ \\  | (__ / _ \\| '  \\ | '  \\ / _` || ' \\ / _` |(_-<
            |_| \\___/| .__/   \\___|\\___/|_|_|_||_|_|_|\\__,_||_||_|\\__,_|/__/
                     |_|                                                    
                        Top 10 most frequently used commands
__________________________________________________________________________________________
------------------------------------------------------------------------------------------

""".strip()
    cli_wrap.output.append(top_commands_title)

    for i, (item, perc) in enumerate(command_percentages):
            i += 1
            bar = cli_wrap.create_scaled_bar(perc)
            padded_item = cli_wrap.pad_text(f"{i}. {item}", FILE_COLOR, 30)
            cli_wrap.output.append(f"{padded_item:>50} | {bar} | {perc:5.1f}%") 

    top_files_title = """
__________________________________________________________________________________________
------------------------------------------------------------------------------------------
                         _____              ___  _  _          
                        |_   _|___  _ __   | __|(_)| | ___  ___
                          | | / _ \\| '_ \\  | _| | || |/ -_)(_-<
                          |_| \\___/| .__/  |_|  |_||_|\\___|/__/
                                   |_|                         
                          Top 10 most frequently accessed files
__________________________________________________________________________________________
------------------------------------------------------------------------------------------
""".strip()
    cli_wrap.output.append(top_files_title)

    for i, (item, perc) in enumerate(file_percentages):
            i += 1
            bar = cli_wrap.create_scaled_bar(perc)
            padded_item = cli_wrap.pad_text(f"{i}. {item}", FILE_COLOR, 30)
            cli_wrap.output.append(f"{padded_item:>50} | {bar} | {perc:5.1f}%") 

    totals = f"\nTotal commands: {total_commands}\nTotal files found: {total_files}"
    cli_wrap.output.append(totals)

    outer_box = cli_wrap.create_outer_box(cli_wrap.output, cli_wrap.box_width)
    print('\n'.join(outer_box))
            
if __name__ == "__main__":
    main()
