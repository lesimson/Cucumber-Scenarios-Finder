# -*- coding: utf-8 -*-
import sublime, sublime_plugin
import os
import re
import codecs

class CucumberBaseCommand(sublime_plugin.WindowCommand, object):
  def __init__(self, window):
    sublime_plugin.WindowCommand.__init__(self, window)
    self.load_settings()

  def load_settings(self):
    self.settings = sublime.load_settings("CucumberScenarioFinder.sublime-settings")
    self.features_path = self.settings.get('cucumber_features_path')  # Default is "features"
    self.scenario_pattern = self.settings.get('cucumber_scenario_pattern')    # Default is '.*_steps.*\.rb'

  def find_scenario_in_file(self, root, f_name):
    pattern = re.compile(r'(.*Scenario:.*)')
    step_file_path = os.path.join(root, f_name)
    with codecs.open(step_file_path, encoding='utf-8') as f:
      index = 0
      for line in f:
        match = re.match(pattern, line)
        if match:
          self.scenarios.append((match.group().strip(), index, step_file_path))
        index += 1

  def find_all_scenarios(self, file_name=None):
    self.scenarios = []
    folders = self.window.folders()
    if file_name == None:
      for folder in folders:
        for path in os.listdir(folder) + ['.']:
          full_path = os.path.join(folder, path)
          if path == self.features_path:
            self.step_files = []
            for root, dirs, files in os.walk(full_path, followlinks=True):
              for f_name in files:
                if re.match(self.scenario_pattern, f_name):
                  self.step_files.append((f_name, os.path.join(root, f_name)))
                  self.find_scenario_in_file(root, f_name)
    else:
      root = os.path.join(file_name)
      self.find_scenario_in_file(root, file_name)
              

  def scenario_found(self, index):
    if index >= 0:
      file_path = self.scenarios[index][2]
      view = self.window.open_file(file_path)
      self.active_ref = (view, self.scenarios[index][1])
      self.mark_step()

class CucumberScenarioFinderCommand(CucumberBaseCommand):
  def __init__(self, window):
    CucumberBaseCommand.__init__(self, window)

  def run(self, file_name=None):
    self.list_scenarios()

  def list_scenarios(self):
    self.find_all_scenarios()
    scenarios_only = [x[0] for x in self.scenarios]
    self.window.show_quick_panel(scenarios_only, self.scenario_found)

class CucumberScenarioFinderLocalCommand(CucumberBaseCommand):
  def __init__(self, window):
      CucumberBaseCommand.__init__(self, window)

  def run(self, file_name=None):
      self.list_scenarios()

  def list_scenarios(self):
    view = self.window.active_view()
    self.find_all_scenarios(view.file_name())
    scenarios_only = [x[0] for x in self.scenarios]
    self.window.show_quick_panel(scenarios_only, self.scenario_found)