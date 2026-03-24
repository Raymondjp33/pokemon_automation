import 'package:json_annotation/json_annotation.dart';

import 'display_content.model.dart';

part 'stream_data.model.g.dart';

@JsonSerializable(explicitToJson: true)
class StreamData {
  bool away;

  DisplayContent? switch1Content;
  DisplayContent? switch2Content;
  DisplayContent? switch3Content;

  StreamData({
    required this.away,
    this.switch1Content,
    this.switch2Content,
    this.switch3Content,
  });

  factory StreamData.fromJson(Map<String, dynamic>? json) {
    if (json == null) throw Exception('StreamData: json was null');
    try {
      return _$StreamDataFromJson(json);
    } catch (e, stack) {
      throw 'StreamData.fromJson: $e, $stack';
    }
  }

  Map<String, dynamic> toJson() {
    Map<String, dynamic> json = _$StreamDataToJson(this);
    return json;
  }
}
