@JS()
library media_devices_interop;

import 'package:js/js.dart';
import 'package:js/js_util.dart';
import '../../widgets/state_view_widget.dart';
import 'control_panel_view.dart';
import 'package:web/web.dart' as web;

import 'dart:ui_web' as ui_web;

class ControlPanel extends StateView<ControlPanelState> {
  ControlPanel({super.key})
      : super(
          stateBuilder: (context) => ControlPanelState(context),
          view: ControlPanelView(),
        );
}

class ControlPanelState extends StateProvider<ControlPanel> {
  ControlPanelState(super.context) {
    loadControlPanel();
  }

  web.HTMLVideoElement? video1;
  String? viewType1;

  web.HTMLVideoElement? video2;
  String? viewType2;

  List<dynamic> videoDevices = [];

  Future<void> loadControlPanel() async {
    await getDevices();
    loadDevices();
  }

  Future<void> requestPermission() async {
    try {
      await promiseToFuture(
        callMethod(
          getProperty(web.window.navigator, 'mediaDevices'),
          'getUserMedia',
          [
            jsify({
              'video': {"width": 1280, "height": 720},
            }),
          ],
        ),
      );
    } catch (e) {
      print('Permission denied or error: $e');
    }
  }

  Future<void> loadDevices() async {
    for (final device in videoDevices) {
      if (device.label != 'USB Video (534d:2109)' &&
          device.label != 'USB3.0 Capture (345f:2130)') {
        continue;
      }

      final mediaStream = await promiseToFuture(
        callMethod(
          getProperty(web.window.navigator, 'mediaDevices'),
          'getUserMedia',
          [
            jsify({
              'video': {
                'deviceId': device.deviceId,
                "width": 1280,
                "height": 720,
              },
            }),
          ],
        ),
      );
      final video = web.HTMLVideoElement()
        ..autoplay = true
        ..muted = true
        ..style.width = '100%'
        ..style.height = '100%'
        ..style.objectFit = 'contain'
        ..srcObject = mediaStream;

      final viewType = 'video-element-${DateTime.now().millisecondsSinceEpoch}';
      ui_web.platformViewRegistry
          .registerViewFactory(viewType, (int viewId) => video);

      if (device.label != 'USB Video (534d:2109)') {
        video2 = video;
        viewType2 = viewType;
      } else {
        video1 = video;
        viewType1 = viewType;
      }
    }

    notifyListeners();
  }

  Future<void> getDevices() async {
    await requestPermission();

    videoDevices = await promiseToFuture<List<dynamic>>(
      callMethod(
        getProperty(web.window.navigator, 'mediaDevices'),
        'enumerateDevices',
        [],
      ),
    );

    notifyListeners();
  }
}
