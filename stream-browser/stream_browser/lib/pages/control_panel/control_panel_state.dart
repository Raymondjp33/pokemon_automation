@JS()
library media_devices_interop;

import 'dart:convert';

import 'package:js/js.dart';
import 'package:js/js_util.dart';
import '../../widgets/state_view_widget.dart';
import 'control_panel_view.dart';
import 'dart:html' as html;

import 'dart:ui' as ui;

@JS('navigator.mediaDevices.getUserMedia')
external dynamic _getUserMedia(dynamic constraints);

@JS('navigator.mediaDevices.enumerateDevices')
external dynamic _enumerateDevices();

@JS()
@anonymous
class MediaDeviceInfo {
  external String get deviceId;
  external String get kind;
  external String get label;
}

@JS()
@anonymous
class InputDeviceInfo {
  external String get deviceId;
  external String get kind;
  external String get label;
}

class ControlPanel extends StateView<ControlPanelState> {
  ControlPanel({super.key})
      : super(
          stateBuilder: (context) => ControlPanelState(context),
          view: ControlPanelView(),
        );
}

class ControlPanelState extends StateProvider<ControlPanel> {
  ControlPanelState(super.context) {
    loadDevices();
  }

  html.VideoElement? video;
  String? viewType;

  List<String> videoDevices = [];

  Future<void> loadDevices() async {
    getDevices();
    // videoDevices = await getVideoInputDevices();
  }

  Future<void> requestPermission() async {
    try {
      await promiseToFuture(
        callMethod(
          getProperty(html.window.navigator, 'mediaDevices'),
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

  Future<List<dynamic>> getDevices() async {
    await requestPermission();

    List<dynamic> devices = await promiseToFuture<List<dynamic>>(
      callMethod(
        getProperty(html.window.navigator, 'mediaDevices'),
        'enumerateDevices',
        [],
      ),
    );

    devices = devices.map((e) async {
      // try {
      //   devices
      //       .cast<InputDeviceInfo>()
      //       .where((d) => d.kind == 'videoinput')
      //       .toList();
      // } catch (e) {
      //   print('here and error $e');
      // }

      if (e.label == 'USB Video (534d:2109)') {
        final mediaStream = await promiseToFuture(
          callMethod(
            getProperty(html.window.navigator, 'mediaDevices'),
            'getUserMedia',
            [
              jsify({
                'video': {'deviceId': e.deviceId},
              }),
            ],
          ),
        );
        video = html.VideoElement()
          ..autoplay = true
          ..muted = true
          ..style.width = '100%'
          ..style.height = '100%'
          ..style.objectFit = 'contain'
          ..srcObject = mediaStream;

        viewType = 'video-element-${DateTime.now().millisecondsSinceEpoch}';
        // ignore: undefined_prefixed_name
        ui.platformViewRegistry
            .registerViewFactory(viewType!, (int viewId) => video!);
        notifyListeners();
      }

      return e.label;
    }).toList();

    return devices;
  }

  Future<dynamic> getUserMedia(String deviceId) {
    final constraints = {
      'video': {'deviceId': deviceId},
    };
    return promiseToFuture<dynamic>(_getUserMedia(jsify(constraints)));
  }
}
