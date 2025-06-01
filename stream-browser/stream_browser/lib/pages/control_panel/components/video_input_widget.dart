import 'package:flutter/material.dart';
import 'package:resizable_widget/resizable_widget.dart';
import 'package:web/web.dart' as web;

class VideoInputWidget extends StatelessWidget {
  const VideoInputWidget({
    required this.video,
    required this.viewType,
    super.key,
  });

  final web.HTMLVideoElement? video;
  final String? viewType;

  @override
  Widget build(BuildContext context) {
    return viewType != null
        ? Container(
            constraints: BoxConstraints(maxHeight: 300, maxWidth: 600),
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
                      child: HtmlElementView(viewType: viewType!),
                    ),
                  ),
                ),
              ],
            ),
          )
        : Text('Unable to load');
  }
}
