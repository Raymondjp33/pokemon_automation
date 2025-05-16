import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:resizable_widget/resizable_widget.dart';

import 'control_panel_state.dart';

class ControlPanelView extends StatelessWidget {
  const ControlPanelView({super.key});

  @override
  Widget build(BuildContext context) {
    final state = context.watch<ControlPanelState>();
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            if (state.viewType != null)
              Container(
                constraints: BoxConstraints(maxHeight: 700),
                child: ResizableWidget(
                  isHorizontalSeparator: false,
                  isDisabledSmartHide: false,
                  children: [
                    Container(
                      child: AspectRatio(
                        aspectRatio: 16 / 9,
                        child: GestureDetector(
                          onTapDown: (details) {
                            print(
                              'Tap down at X: ${details.localPosition.dx} Y: ${details.localPosition.dy}',
                            );
                          },
                          child: HtmlElementView(viewType: state.viewType!),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            for (String name in state.videoDevices) Text(name),
            GestureDetector(
              child: Container(
                width: 100,
                height: 50,
                color: Colors.grey,
                child: Center(child: Text('press')),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
