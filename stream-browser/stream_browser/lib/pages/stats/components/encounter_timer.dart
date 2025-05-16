import 'package:flutter/material.dart';

import '../../../constants/app_styles.dart';

class EncounterTimer extends StatelessWidget {
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
  Widget build(BuildContext context) {
    if (startTime == null) {
      return Container();
    }

    DateTime now = DateTime.now();
    Duration timeDifference = Duration(
      milliseconds: endTime ?? now.millisecondsSinceEpoch - startTime!.toInt(),
    );
    return Text(
      formatDuration(timeDifference),
      style: AppTextStyles.pokePixel(fontSize: fontSize?.toDouble() ?? 24),
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
