import 'package:json_annotation/json_annotation.dart';

import 'display_content.model.dart';

part 'stream_data.model.g.dart';

@JsonSerializable(explicitToJson: true)
class StreamData {
  bool away;

  @JsonKey(name: 'left')
  DisplayContent? switch1Content;
  @JsonKey(name: 'right')
  DisplayContent? switch2Content;

  StreamData({
    required this.away,
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
