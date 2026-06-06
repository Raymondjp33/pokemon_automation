import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:web/web.dart' as web;
import '../../services/file_provider.dart';
import 'components/script_manager_widget.dart';
import 'components/stream_data_info.dart';
import 'components/switch_controller_widget.dart';
import 'components/video_input_widget.dart';
import 'control_panel_state.dart';

class ControlPanelView extends StatefulWidget {
  const ControlPanelView({super.key});

  @override
  State<ControlPanelView> createState() => _ControlPanelViewState();
}

class _ControlPanelViewState extends State<ControlPanelView> {
  int _sw = 1;

  web.HTMLVideoElement? _activeVideo(ControlPanelState state) =>
      _sw == 1 ? state.video1 : _sw == 2 ? state.video2 : state.video3;

  String? _activeViewType(ControlPanelState state) =>
      _sw == 1 ? state.viewType1 : _sw == 2 ? state.viewType2 : state.viewType3;

  @override
  Widget build(BuildContext context) {
    final fileProvider = context.watch<FileProvider>();
    final state = context.watch<ControlPanelState>();

    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          image: DecorationImage(
            image: AssetImage('assets/images/full_cloud_background.png'),
            fit: BoxFit.cover,
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Tab bar
            Padding(
              padding: const EdgeInsets.fromLTRB(12, 12, 12, 0),
              child: Row(
                children: [
                  for (int n = 1; n <= 3; n++)
                    _SwitchTab(
                      label: 'Switch $n',
                      active: _sw == n,
                      onTap: () => setState(() => _sw = n),
                    ),
                ],
              ),
            ),
            // Content
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(12),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Video + logs
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        VideoInputWidget(
                          video: _activeVideo(state),
                          viewType: _activeViewType(state),
                        ),
                        StreamDataInfo(logs: fileProvider.logs1),
                      ],
                    ),
                    const SizedBox(width: 16),
                    // Script manager + controller
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        ScriptManagerWidget(switchNum: _sw),
                        const SizedBox(height: 12),
                        SwitchControllerWidget(switchNum: _sw),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _SwitchTab extends StatelessWidget {
  const _SwitchTab({
    required this.label,
    required this.active,
    required this.onTap,
  });

  final String label;
  final bool active;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.only(right: 4),
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
        decoration: BoxDecoration(
          color: active ? const Color(0xFF4C6CBF) : const Color(0xFF1E2A4A),
          border: Border.all(
            color: const Color(0xFF4C6CBF),
            width: active ? 2 : 1,
          ),
          borderRadius: const BorderRadius.only(
            topLeft: Radius.circular(6),
            topRight: Radius.circular(6),
          ),
        ),
        child: Text(
          label,
          style: TextStyle(
            color: active ? Colors.white : Colors.white54,
            fontFamily: 'Minecraft',
            fontSize: 12,
            fontWeight: active ? FontWeight.bold : FontWeight.normal,
          ),
        ),
      ),
    );
  }
}
