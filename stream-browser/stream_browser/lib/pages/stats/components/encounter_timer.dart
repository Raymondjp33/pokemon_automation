import 'dart:async';

import 'package:flutter/material.dart';

import '../../../constants/app_styles.dart';

class EncounterTimer extends StatefulWidget {
  const EncounterTimer({
    required this.startTime,
    required this.endTime,
    this.fontSize,
    super.key,
  });

  final int? startTime;
  final int? endTime;
  final int? fontSize;

  @override
  State<EncounterTimer> createState() => _EncounterTimerState();
}

class _EncounterTimerState extends State<EncounterTimer> {
  late Timer _timer;
  @override
  void initState() {
    super.initState();
    _timer = Timer.periodic(
      const Duration(seconds: 1),
      (Timer timer) {
        if (widget.endTime == null && widget.startTime != null) {
          setState(() {});
        }
      },
    );
  }

  @override
  void dispose() {
    _timer.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (widget.startTime == null) {
      return Container();
    }

    DateTime now = DateTime.now();
    Duration timeDifference = Duration(
      milliseconds: widget.endTime ??
          now.millisecondsSinceEpoch - widget.startTime!.toInt(),
    );
    return Text(
      formatDuration(timeDifference),
      style:
          AppTextStyles.pokePixel(fontSize: widget.fontSize?.toDouble() ?? 24),
    );
  }

  String formatDuration(Duration duration) {
    int days = duration.inDays;
    int hours = duration.inHours % 24;
    int minutes = duration.inMinutes % 60;
    int seconds = duration.inSeconds % 60;

    final parts = <String>[];
    if (days > 0) parts.add('${days}d');
    if (hours > 0) parts.add('${hours}h');
    if (minutes > 0) parts.add('${minutes}m');
    if (seconds > 0 || parts.isEmpty) parts.add('${seconds}s');

    return parts.join(' ');
  }
}
