import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../services/file_provider.dart';
import 'components/stream_data_info.dart';
import 'components/video_input_widget.dart';
import 'control_panel_state.dart';

class ControlPanelView extends StatelessWidget {
  const ControlPanelView({super.key});

  @override
  Widget build(BuildContext context) {
    final fileProvider = context.watch<FileProvider>();
    final state = context.watch<ControlPanelState>();
    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          image: DecorationImage(
            image: AssetImage(
              'assets/images/full_cloud_background.png',
            ),
            fit: BoxFit.cover,
          ),
        ),
        child: Center(
          child: SingleChildScrollView(
            child: Row(
              children: [
                Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.start,
                      children: [
                        VideoInputWidget(
                          video: state.video1,
                          viewType: state.viewType1,
                        ),
                        StreamDataInfo(
                          logs: fileProvider.logs1,
                        ),
                      ],
                    ),
                    Row(
                      children: [
                        VideoInputWidget(
                          video: state.video2,
                          viewType: state.viewType2,
                        ),
                      ],
                    ),
                    GestureDetector(
                      onTap: () => fileProvider.emitProcess(),
                      child: Container(
                        width: 100,
                        height: 50,
                        color: Colors.grey,
                        child: Center(child: Text('press')),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
