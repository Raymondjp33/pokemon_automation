import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../services/file_provider.dart';

class StreamDataInfo extends StatelessWidget {
  const StreamDataInfo({super.key});

  @override
  Widget build(BuildContext context) {
    final fileProvider = context.watch<FileProvider>();

    final streamData = fileProvider.streamData?.toJson();

    if (streamData == null) {
      return Container();
    }
    return Column(
      children: [
        for (String log in fileProvider.logs) Text(log),

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
