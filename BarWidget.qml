import QtQuick
import qs.Ui

BarWidget {
  id: root
  moduleName: "io.github.tuxclaw.clip"

  implicitWidth: button.implicitWidth
  implicitHeight: button.implicitHeight

  WidgetButton {
    id: button
    anchors.fill: parent
    bar: root.bar
    text: "󰅌"
    tooltipText: "Clip"
    horizontalMargin: 7.5
    onPressed: {
      if (root.bar) root.bar.run("omarchy-shell shell toggle io.github.tuxclaw.clip")
    }
  }
}
