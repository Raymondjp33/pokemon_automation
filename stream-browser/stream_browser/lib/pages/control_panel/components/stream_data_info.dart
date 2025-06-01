import 'package:flutter/material.dart';

class StreamDataInfo extends StatelessWidget {
  const StreamDataInfo({required this.logs, super.key});

  final List<String> logs;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        for (String log in logs) Text(log),

        // for (MapEntry entry in streamData.entries)
        //   Container(
        //     width: 400,
        //     child: Row(
        //       mainAxisAlignment: MainAxisAlignment.spaceBetween,
        //       children: [Text('${entry.key}'), Text('${entry.value}')],
        //     ),
        //   ),
      ],
    );
  }
}
