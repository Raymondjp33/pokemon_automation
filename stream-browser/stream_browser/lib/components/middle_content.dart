import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';

import '../constants/app_styles.dart';
import '../services/file_provider.dart';

class MiddleContent extends StatelessWidget {
  const MiddleContent({super.key});

  @override
  Widget build(BuildContext context) {
    final fileProvider = context.watch<FileProvider>();
    DateTime now = DateTime.now();
    int? startTime = fileProvider.streamData?.streamStarttime.toInt();

    Duration timeDifference = Duration(
      milliseconds: now.millisecondsSinceEpoch -
          (startTime ?? now.millisecondsSinceEpoch),
    );

    return Column(
      children: [
        Text(
          formatDateTime(now),
          style: AppTextStyles.minecraftTen(fontSize: 32),
        ),
        Spacer(),
        Text(
          'Stream Runtime',
          style: AppTextStyles.pokePixel(fontSize: 32),
        ),
        Text(
          formatDuration(timeDifference),
          style: AppTextStyles.pokePixel(fontSize: 32),
        ),
        Text(
          fileProvider.streamData?.away ?? true ? 'IM AWAY' : ' IM HERE',
          style: AppTextStyles.minecraftTen(fontSize: 64),
        ),
      ],
    );
  }
}

String formatDateTime(DateTime dateTime) {
  return '${DateFormat('hh:mm:ssa').format(dateTime)} EST';
}

String formatDuration(Duration duration) {
  int days = duration.inDays;
  int hours = duration.inHours % 24;

  final parts = <String>[];
  if (days > 0) parts.add('${days}d');
  if (hours > 0) parts.add('${hours}h');

  return parts.join(' ');
}
